import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import set_final_models
import sync_friendly_labels


class PresetTests(unittest.TestCase):
    def test_final_eight_model_presets(self):
        self.assertEqual(len(set_final_models.PRESETS), 8)
        aliases = [x[0] for x in set_final_models.PRESETS]
        self.assertEqual(len(set(aliases)), 8)
        self.assertFalse(set(aliases) & set_final_models.RETIRED)
        self.assertEqual([x[2] for x in set_final_models.PRESETS].count('high'), 2)
        self.assertEqual(len(sync_friendly_labels.LABELS), 8)
        self.assertEqual(set(aliases), set(sync_friendly_labels.LABELS))

    def test_env_transform_is_idempotent(self):
        raw = '''UPSTREAM=codex
MODEL_MAP=claude-opus-sol61-low=gpt-6.1-sol,claude-sonnet-sol-low=gpt-6-sol
MODEL_EFFORT_MAP=claude-opus-sol61-low=low,claude-sonnet-sol-low=low
MODEL_DISPLAY_MAP=claude-opus-sol61-low=old,claude-sonnet-sol-low=old
ANTHROPIC_DISCOVERY_MODELS=opus,sonnet,haiku,claude-sonnet-sol-low
USER_OTHER_FLAG=keep
'''
        a = set_final_models.transform_env(raw)
        b = set_final_models.transform_env(a)
        self.assertEqual(a, b)
        self.assertIn('USER_OTHER_FLAG=keep', a)
        self.assertIn('MODEL_MAP=claude-opus-sol61-low=gpt-6.1-sol', a)
        self.assertNotIn('claude-sonnet-sol-low', a)
        self.assertNotIn('claude-haiku-luna-none', a)
        for alias, model, effort, label in set_final_models.PRESETS:
            self.assertIn(f'{alias}={model}', a)
            self.assertIn(f'{alias}={effort}', a)
            self.assertIn(alias, a)

    def test_does_not_silently_accept_missing_source_patch(self):
        with self.assertRaisesRegex(RuntimeError, 'not installed'):
            set_final_models.transform_env('UPSTREAM=codex\n')

    def test_duplicate_controlled_keys_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Duplicate'):
            set_final_models.transform_env('MODEL_MAP=a=b\nMODEL_MAP=x=y\n')

    def test_labels_only_modify_names(self):
        meta = {'claudeDesktopModelRoutes': {key: {'model': key, 'supports1m': False} for key in sync_friendly_labels.LABELS}}
        new_meta, changed = sync_friendly_labels.label_provider(meta)
        self.assertEqual(changed, 8)
        self.assertEqual(meta['claudeDesktopModelRoutes']['claude-haiku-luna-low'].get('labelOverride'), None)
        self.assertEqual(new_meta['claudeDesktopModelRoutes']['claude-haiku-luna-low']['labelOverride'], 'GPT-6 Luna · Low')
        self.assertEqual(new_meta['claudeDesktopModelRoutes']['claude-haiku-luna-low']['model'], 'claude-haiku-luna-low')
        profile = {'inferenceModels': list(sync_friendly_labels.LABELS)}
        new_profile, n = sync_friendly_labels.label_profile(profile)
        self.assertEqual(n, 8)
        self.assertTrue(all(isinstance(v, dict) for v in new_profile['inferenceModels']))

if __name__ == '__main__':
    unittest.main()
