"""
WhoLetTheBuggOut Test

Tests the behaviour of the bug


"""

import unittest
from enum import Enum, auto
from typing import List, override
from unittest.mock import Mock, call, patch

from SyedPabon import Role, Status, WhoLetTheBuggOut


class WhoLetTheBuggOutTest(WhoLetTheBuggOut):
    def __init__(self):
        super().__init__()
        self.bt = self.build_tree()  # Build the tree structure here

    @override
    def do_turn(self):  # type: ignore
        return self.bt.tick(self)

    # Actions/Conditions used in the BT, which we will mock
    @override
    def needs_organs(self):
        return False

    @override
    def grow_organs_action(self):  # type: ignore
        return Status.SUCCESS

    @override
    def behavior_horizontal_expansion(self):  # type: ignore
        return Status.SUCCESS

    @override
    def behavior_vertical_scouting(self):  # type: ignore
        return Status.SUCCESS

    @override
    def behavior_cluster_management(self):  # type: ignore
        return Status.SUCCESS

    @override
    def behavior_vertical_filling(self):  # type: ignore
        return Status.SUCCESS

    @override
    def behavior_harvesting(self):  # type: ignore
        return Status.SUCCESS


# =============================================================
# UNIT TEST CLASS
# =============================================================


class TestBehaviorTreeStructure(unittest.TestCase):
    def setUp(self):
        # Create a creature instance. Its methods will be mocked by the tests.
        self.bug = WhoLetTheBuggOutTest()

    @patch.object(WhoLetTheBuggOutTest, "needs_organs")
    @patch.object(WhoLetTheBuggOutTest, "grow_organs_action")
    @patch.object(WhoLetTheBuggOutTest, "behavior_horizontal_expansion")
    def test_priority_1_organ_growth_takes_precedence(
        self, mock_expand, mock_grow, mock_needs_organs
    ):
        """Test that Organ Growth runs if the condition is met, regardless of role."""

        # 1. Setup: Needs organs, but is also a HORIZONTAL_EXPANDER (a high priority role).
        mock_needs_organs.return_value = True
        mock_grow.return_value = Status.SUCCESS
        self.bug.role = Role.HORIZONTAL_EXPANDER

        # 2. Execute
        result = self.bug.do_turn()

        # 3. Assertions
        self.assertEqual(result, Status.SUCCESS)
        mock_needs_organs.assert_called_once()
        mock_grow.assert_called_once()
        mock_expand.assert_not_called()  # Role action should be skipped

    @patch.object(WhoLetTheBuggOutTest, "needs_organs")
    @patch.object(WhoLetTheBuggOutTest, "behavior_horizontal_expansion")
    def test_priority_2_horizontal_expander_runs(self, mock_expand, mock_needs_organs):
        """Test the Horizontal Expander sequence runs if no organs are needed."""

        # 1. Setup: No organs needed. Is HORIZONTAL_EXPANDER.
        mock_needs_organs.return_value = False
        mock_expand.return_value = Status.SUCCESS
        self.bug.role = Role.HORIZONTAL_EXPANDER

        # 2. Execute
        result = self.bug.do_turn()

        # 3. Assertions
        self.assertEqual(result, Status.SUCCESS)
        mock_needs_organs.assert_called_once()  # Must check this first
        mock_expand.assert_called_once()  # Then execute this role

    @patch.object(WhoLetTheBuggOutTest, "needs_organs")
    @patch.object(WhoLetTheBuggOutTest, "behavior_harvesting")
    @patch.object(WhoLetTheBuggOutTest, "behavior_horizontal_expansion")
    @patch.object(WhoLetTheBuggOutTest, "behavior_vertical_scouting")
    def test_priority_3_harvester_runs_last(
        self, mock_scout, mock_expand, mock_harvest, mock_needs_organs
    ):
        """Test that the HARVESTER role runs only after all others fail the Condition."""

        # 1. Setup: No organs needed. Is HARVESTER.
        mock_needs_organs.return_value = False
        mock_harvest.return_value = Status.SUCCESS
        self.bug.role = Role.HARVESTER

        # 2. Execute
        result = self.bug.do_turn()

        # 3. Assertions
        self.assertEqual(result, Status.SUCCESS)

        # Check all conditions/actions before HARVESTER were checked/skipped
        mock_needs_organs.assert_called_once()
        mock_expand.assert_not_called()  # Sequence 2 (Expander) Condition fails
        mock_scout.assert_not_called()  # Sequence 3 (Scout) Condition fails
        # ... and so on for CLUSTER_MANAGER and VERTICAL_FILLER (not explicitly mocked here, but implied)

        # HARVESTER sequence must run
        mock_harvest.assert_called_once()

    @patch.object(WhoLetTheBuggOutTest, "needs_organs")
    @patch.object(WhoLetTheBuggOutTest, "behavior_cluster_management")
    @patch.object(WhoLetTheBuggOutTest, "behavior_horizontal_expansion")
    @patch.object(WhoLetTheBuggOutTest, "behavior_vertical_scouting")
    def test_selector_finds_correct_role_in_middle(
        self, mock_scout, mock_expand, mock_cluster, mock_needs_organs
    ):
        """Test that the Selector correctly skips the first few role checks and finds the target role."""

        # 1. Setup: No organs needed. Is CLUSTER_MANAGER (3rd role in list).
        mock_needs_organs.return_value = False
        mock_cluster.return_value = Status.SUCCESS
        self.bug.role = Role.CLUSTER_MANAGER

        # 2. Execute
        result = self.bug.do_turn()

        # 3. Assertions
        self.assertEqual(result, Status.SUCCESS)

        # Check that roles before CLUSTER_MANAGER were skipped (Condition failed)
        mock_expand.assert_not_called()
        mock_scout.assert_not_called()

        # CLUSTER_MANAGER must run
        mock_cluster.assert_called_once()


if __name__ == "__main__":
    print("Running WhoLetTheBuggOutTest Behavior Tree Structure Tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBehaviorTreeStructure)
    unittest.TextTestRunner(verbosity=2).run(suite)
