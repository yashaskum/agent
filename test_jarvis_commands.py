import asyncio
import unittest
from unittest.mock import patch

from jarvis_brain import JarvisBrain


class JarvisCommandTests(unittest.TestCase):
    def run_command(self, brain, text):
        return asyncio.run(brain.process_input(text))

    def test_process_listing(self):
        result = self.run_command(JarvisBrain(), "show running processes")
        self.assertEqual(result["action"], "process_list")
        self.assertIsInstance(result["data"], list)

    def test_power_actions_require_confirmation(self):
        brain = JarvisBrain()
        result = self.run_command(brain, "restart")
        self.assertEqual(result["status"], "awaiting_confirmation")
        self.assertEqual(result["data"]["pending_action"], "restart")

        cancelled = self.run_command(brain, "cancel")
        self.assertEqual(cancelled["action"], "confirmation_cancelled")

    def test_confirmed_power_action_calls_handler(self):
        brain = JarvisBrain()
        with patch("system_control.power_action", return_value={"success": True, "message": "done"}) as action:
            self.run_command(brain, "shutdown")
            result = self.run_command(brain, "confirm")
        action.assert_called_once_with("shutdown")
        self.assertEqual(result["status"], "executed")

    def test_unknown_application_is_rejected(self):
        result = self.run_command(JarvisBrain(), "launch definitely-not-an-app")
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
