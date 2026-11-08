import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from review_ui import ReviewStore, read


class ReviewStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.directory=Path(self.tmp.name)
        issue={'issue_id':'one','item_id':'0013','field':'prompt','index':None,
               'translation':'Original','suggestion':'Vorschlag'}
        issues=[issue,{**issue,'issue_id':'two'}]
        (self.directory/'human-review-queue.jsonl').write_text(''.join(json.dumps(q)+'\n' for q in issues))
        (self.directory/'human-decisions.jsonl').write_text('')
        self.store=ReviewStore(self.directory)

    def payload(self, **changes):
        return {'revision':self.store.revision(),'decision':{'issue_id':'one','decision':'accept',
                'reviewer':'Test','reviewer_role':'Test fixture','reason':'Test only',
                'final_text':'Vorschlag','evidence':[],**changes}}

    def test_save_updates_one_ledger_entry(self):
        self.store.save(self.payload())
        self.store.save(self.payload(reason='Updated justification'))
        ledger=read(self.directory/'human-decisions.jsonl')
        self.assertEqual(len(ledger),1)
        self.assertEqual(ledger[0]['reason'],'Updated justification')
        self.assertIn('+00:00',ledger[0]['decided_at'])

    def test_concurrent_update_is_rejected(self):
        stale=self.payload();self.store.save(self.payload())
        with self.assertRaisesRegex(ValueError,'inzwischen'):
            self.store.save(stale)

    def test_conflicting_field_decisions_rejected(self):
        self.store.save(self.payload())
        with self.assertRaisesRegex(ValueError,'andere Entscheidung'):
            self.store.save(self.payload(issue_id='two',decision='reject',final_text='Original'))

    def test_decision_contract(self):
        for change in [{'reviewer':''},{'reason':''},{'decision':'reject'},
                       {'final_text':''},{'issue_id':'missing'},{'decision':'made-up'}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.store.save(self.payload(**change))
        self.store.save(self.payload(decision='defer',final_text=None))
        self.assertIsNone(read(self.directory/'human-decisions.jsonl')[0]['final_text'])

    def test_human_finding_on_unflagged_item_is_separate_and_decidable(self):
        source = {'id':'unflagged','prompt':'CCTV clip'}
        target = {'id':'unflagged','prompt':'CCTV-Clip'}
        (self.directory/'upstream/data').mkdir(parents=True)
        (self.directory/'upstream/data/items.jsonl').write_text(json.dumps(source)+'\n')
        (self.directory/'translated.jsonl').write_text(json.dumps(target)+'\n')
        before = (self.directory/'human-review-queue.jsonl').read_bytes()
        with patch('review_ui.ROOT', self.directory):
            result = self.store.add_finding({'revision':self.store.revision(), 'finding':{
                'item_id':'unflagged','field':'prompt','index':None,'reason':'Context requires translation',
                'reporter':'Test','reporter_role':'Test fixture','suggestion':'Überwachungsvideo',
                'term':'CCTV','rule':'Distinguish camera footage from broadcaster'}})
            finding = result['finding']
            self.assertEqual(finding['origin'],'human')
            self.assertEqual(len(finding['related_locations']),1)
            self.assertEqual((self.directory/'human-review-queue.jsonl').read_bytes(),before)
            self.store.save(self.payload(issue_id=finding['issue_id'],final_text='Überwachungsvideo'))
            self.assertEqual(read(self.directory/'human-decisions.jsonl')[0]['issue_id'],finding['issue_id'])
            (self.directory/'translated.jsonl').write_text(json.dumps({**target,'prompt':'Changed'})+'\n')
            with self.assertRaisesRegex(ValueError,'Stale'):
                self.store.issues()
