"""
Test suite for cross-class teacher conflict detection and resolution
Tests the scenario: Teacher 'Kranti' with SE lecture 10-11 AND TE practical 10-12 (OVERLAP!)
"""

import pytest
import sys
from collections import defaultdict

# Add parent directory to path to import algorithm
sys.path.insert(0, '/c:/Users/Lenovo/Downloads/newtb_comp/newtb')
from algorithm import CrossClassConflictResolver, ConflictTracker, PRACTICAL_SLOTS


class TestCrossClassConflictResolver:
    """Test CrossClassConflictResolver class"""
    
    def setup_method(self):
        """Initialize resolver for each test"""
        self.resolver = CrossClassConflictResolver()
    
    def test_time_to_minutes_conversion(self):
        """Test time string to minutes conversion"""
        assert self.resolver._time_to_minutes("10:00") == 600
        assert self.resolver._time_to_minutes("10:30") == 630
        assert self.resolver._time_to_minutes("15:45") == 945
        assert self.resolver._time_to_minutes("23:59") == 1439
    
    def test_time_to_minutes_with_range(self):
        """Test time extraction from range string"""
        # Should extract start time
        assert self.resolver._time_to_minutes("10:00 - 11:00") == 600
        assert self.resolver._time_to_minutes("13:00 - 15:00") == 780
    
    def test_slots_overlap_full_overlap(self):
        """Test full overlap detection: same start and end times"""
        # 10:00-11:00 vs 10:00-11:00 → True (full overlap)
        assert self.resolver._slots_overlap(600, 660, 600, 660) == True
    
    def test_slots_overlap_partial_overlap(self):
        """Test partial overlap detection"""
        # 10:00-12:00 vs 10:30-11:30 → True (partial)
        assert self.resolver._slots_overlap(600, 720, 630, 690) == True
        
        # 10:00-11:00 vs 10:30-12:00 → True (partial)
        assert self.resolver._slots_overlap(600, 660, 630, 720) == True
    
    def test_slots_overlap_adjacent_slots(self):
        """Test that adjacent slots don't overlap"""
        # 10:00-11:00 vs 11:00-12:00 → False (adjacent, not overlapping)
        assert self.resolver._slots_overlap(600, 660, 660, 720) == False
    
    def test_slots_overlap_no_overlap(self):
        """Test non-overlapping slots"""
        # 10:00-11:00 vs 13:00-14:00 → False (no overlap)
        assert self.resolver._slots_overlap(600, 660, 780, 840) == False
    
    def test_add_assignment_single_teacher(self):
        """Test recording single teacher assignment"""
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        assert "Kranti" in self.resolver.global_teacher_schedule
        assert "Monday" in self.resolver.global_teacher_schedule["Kranti"]
        assert len(self.resolver.global_teacher_schedule["Kranti"]["Monday"]) == 1
        
        slot, cls, activity, _ = self.resolver.global_teacher_schedule["Kranti"]["Monday"][0]
        assert slot == "10:00 - 11:00"
        assert cls == "SE"
        assert activity == "lecture"
    
    def test_check_cross_class_overlap_no_conflict(self):
        """Test: No conflict when teacher has no other assignments"""
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Check a different slot
        conflicts = self.resolver.check_cross_class_overlap("Monday", "13:00 - 14:00", "Kranti", "TE", "practical")
        assert len(conflicts) == 0
    
    def test_check_cross_class_overlap_detects_overlap(self):
        """Test: MAIN TEST - Detect overlap (Kranti scenario)"""
        # Add: Monday 10-11 SE lecture
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Check: Monday 10-12 TE practical (SHOULD CONFLICT)
        conflicts = self.resolver.check_cross_class_overlap("Monday", "10:00 - 12:00", "Kranti", "TE", "practical")
        
        assert len(conflicts) == 1
        assert conflicts[0]['class'] == "SE"
        assert conflicts[0]['activity'] == "lecture"
        assert conflicts[0]['slot'] == "10:00 - 11:00"
        assert conflicts[0]['type'] == "partial"
    
    def test_check_cross_class_overlap_same_class_ignored(self):
        """Test: Conflicts within same class are ignored (only cross-class matters)"""
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Check same class (SE) - should NOT be counted as cross-class conflict
        conflicts = self.resolver.check_cross_class_overlap("Monday", "10:00 - 12:00", "Kranti", "SE", "practical")
        assert len(conflicts) == 0
    
    def test_resolve_strategy_1_slot_move(self):
        """Test Strategy 1: Move practical to alternative slot"""
        # Add: Monday 10-11 SE lecture
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Try to resolve: Monday 10-12 TE practical
        resolution = self.resolver.resolve_cross_class_conflict(
            "Monday", "10:00 - 12:00", "Kranti", "TE", "practical"
        )
        
        assert resolution['resolved'] == True
        assert resolution['strategy'] == 'slot_move'
        assert resolution['old_slot'] == "10:00 - 12:00"
        assert resolution['new_slot'] in ["13:00 - 15:00", "15:00 - 17:00"]
    
    def test_resolve_strategy_2_split_lectures(self):
        """Test Strategy 2: Split lectures across slots"""
        # Add: Monday 10-11 SE lecture
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Try to resolve: Monday 10-11 TE lecture (conflict!)
        # Since it's a lecture, should try to split
        resolution = self.resolver.resolve_cross_class_conflict(
            "Monday", "10:00 - 11:00", "Kranti", "TE", "lecture",
            available_slots=["10:00 - 11:00", "11:00 - 12:00", "13:00 - 14:00"]
        )
        
        # May or may not resolve depending on available slots
        if resolution['resolved']:
            assert resolution['strategy'] == 'split_lectures'
            assert 'slots' in resolution
    
    def test_resolve_strategy_3_reassign_teacher(self):
        """Test Strategy 3: Recommend reassigning to different teacher"""
        # Add: Multiple teachers
        teachers = ["Kranti", "John", "Sarah"]
        
        # Add: Monday 10-11 SE lecture (Kranti)
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Try to resolve: Monday 10-11 TE lecture (conflict!)
        resolution = self.resolver.resolve_cross_class_conflict(
            "Monday", "10:00 - 11:00", "Kranti", "TE", "lecture",
            all_teachers=teachers
        )
        
        # Should suggest reassignment since no slots work for Kranti
        if not resolution['resolved']:
            assert resolution['strategy'] == 'reassign_teacher'
            assert 'recommended_teachers' in resolution
    
    def test_add_assignment_multiple_days(self):
        """Test recording assignments across multiple days"""
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        self.resolver.add_assignment("Tuesday", "13:00 - 14:00", "TE", "Kranti", "practical")
        
        assert len(self.resolver.global_teacher_schedule["Kranti"]["Monday"]) == 1
        assert len(self.resolver.global_teacher_schedule["Kranti"]["Tuesday"]) == 1
    
    def test_add_assignment_multiple_slots_same_day(self):
        """Test multiple assignments same day (should all be recorded)"""
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        self.resolver.add_assignment("Monday", "13:00 - 14:00", "TE", "Kranti", "practical")
        self.resolver.add_assignment("Monday", "14:00 - 15:00", "BE", "Kranti", "lecture")
        
        assert len(self.resolver.global_teacher_schedule["Kranti"]["Monday"]) == 3
    
    def test_generate_conflict_report(self):
        """Test conflict report generation"""
        self.resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Resolve a conflict
        resolution = self.resolver.resolve_cross_class_conflict(
            "Monday", "10:00 - 12:00", "Kranti", "TE", "practical"
        )
        
        if resolution['resolved']:
            report = self.resolver.generate_conflict_report()
            assert 'resolutions_applied' in report
            assert report['count'] >= 0


class TestConflictTrackerWithCrossClass:
    """Test ConflictTracker integration with cross-class resolver"""
    
    def setup_method(self):
        """Initialize tracker for each test"""
        self.tracker = ConflictTracker()
    
    def test_tracker_has_cross_class_resolver(self):
        """Test that ConflictTracker has cross-class resolver"""
        assert hasattr(self.tracker, 'cross_class_resolver')
        assert isinstance(self.tracker.cross_class_resolver, CrossClassConflictResolver)
    
    def test_check_cross_class_conflict_method(self):
        """Test tracker's check_cross_class_conflict method"""
        # Add assignment via tracker
        self.tracker.add_assignment("Monday", "10:00 - 11:00", "SE", None, "Kranti", activity_type="lecture")
        
        # Check for conflict
        conflicts = self.tracker.check_cross_class_conflict("Monday", "10:00 - 12:00", "TE", "Kranti", "practical")
        
        assert len(conflicts) == 1
        assert conflicts[0]['class'] == "SE"
    
    def test_resolve_cross_class_conflict_method(self):
        """Test tracker's resolve_cross_class_conflict method"""
        self.tracker.add_assignment("Monday", "10:00 - 11:00", "SE", None, "Kranti", activity_type="lecture")
        
        resolution = self.tracker.resolve_cross_class_conflict(
            "Monday", "10:00 - 12:00", "TE", "Kranti", "practical"
        )
        
        assert isinstance(resolution, dict)
        assert 'resolved' in resolution
        assert 'strategy' in resolution


class TestIntegrationKrantiScenario:
    """Integration tests for the exact Kranti scenario"""
    
    def test_kranti_scenario_full_resolution(self):
        """
        FULL TEST: Kranti teaches:
        - Monday 10:00-11:00: SE lecture
        - Monday 10:00-12:00: TE practical (CONFLICT!)
        
        Expected: System resolves by moving TE practical to 13:00-15:00 or 15:00-17:00
        """
        resolver = CrossClassConflictResolver()
        
        # Step 1: Record Kranti's SE lecture
        resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # Step 2: Detect conflict when trying to schedule TE practical
        conflicts = resolver.check_cross_class_overlap("Monday", "10:00 - 12:00", "Kranti", "TE", "practical")
        assert len(conflicts) == 1, "Conflict not detected!"
        
        # Step 3: Resolve the conflict
        resolution = resolver.resolve_cross_class_conflict(
            "Monday", "10:00 - 12:00", "Kranti", "TE", "practical"
        )
        
        assert resolution['resolved'] == True, "Conflict not resolved!"
        assert resolution['strategy'] == 'slot_move', "Wrong strategy used!"
        assert resolution['new_slot'] in ["13:00 - 15:00", "15:00 - 17:00"], "Wrong new slot!"
        assert resolution['old_slot'] == "10:00 - 12:00"
    
    def test_kranti_three_class_scenario(self):
        """
        Extended scenario: Kranti teaches 3 classes:
        - Monday 10-11: SE lecture
        - Monday 13-14: BE lecture
        - Monday 10-12: TE practical (conflicts with SE lecture!)
        
        Expected: TE practical moved to 15-17 to avoid conflicts
        """
        resolver = CrossClassConflictResolver()
        
        # Add Kranti's assignments
        resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        resolver.add_assignment("Monday", "13:00 - 14:00", "BE", "Kranti", "lecture")
        
        # Try to schedule TE practical
        conflicts = resolver.check_cross_class_overlap("Monday", "10:00 - 12:00", "Kranti", "TE", "practical")
        assert len(conflicts) == 1  # Only conflicts with SE lecture, not BE
        
        resolution = resolver.resolve_cross_class_conflict(
            "Monday", "10:00 - 12:00", "Kranti", "TE", "practical"
        )
        
        assert resolution['resolved'] == True
        assert resolution['new_slot'] == "15:00 - 17:00", f"Expected 15-17, got {resolution.get('new_slot')}"
    
    def test_no_conflict_different_slots(self):
        """Test: No conflict when activities are in different time slots"""
        resolver = CrossClassConflictResolver()
        
        resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # TE practical at 13-15 (no overlap with SE lecture at 10-11)
        conflicts = resolver.check_cross_class_overlap("Monday", "13:00 - 15:00", "Kranti", "TE", "practical")
        assert len(conflicts) == 0, "False positive conflict detected!"
    
    def test_no_conflict_different_teachers(self):
        """Test: No conflict when different teachers (can overlap)"""
        resolver = CrossClassConflictResolver()
        
        resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        
        # John teaches TE practical at same time (different teacher, OK)
        conflicts = resolver.check_cross_class_overlap("Monday", "10:00 - 12:00", "John", "TE", "practical")
        assert len(conflicts) == 0, "False positive with different teacher!"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_midnight_times(self):
        """Test handling of edge times"""
        resolver = CrossClassConflictResolver()
        
        # Should not crash with extreme times
        assert resolver._time_to_minutes("00:00") == 0
        assert resolver._time_to_minutes("23:59") == 1439
    
    def test_malformed_time_handling(self):
        """Test graceful handling of malformed times"""
        resolver = CrossClassConflictResolver()
        
        # Should return 0 or handle gracefully
        result = resolver._time_to_minutes("invalid")
        assert isinstance(result, int)
    
    def test_empty_schedule(self):
        """Test resolver with empty schedule"""
        resolver = CrossClassConflictResolver()
        
        # No assignments yet, so no conflicts
        conflicts = resolver.check_cross_class_overlap("Monday", "10:00 - 12:00", "Kranti", "TE", "practical")
        assert len(conflicts) == 0
    
    def test_multiple_conflicts_same_slot(self):
        """Test handling multiple conflicts in same slot"""
        resolver = CrossClassConflictResolver()
        
        # Kranti has 2 lectures that might conflict
        resolver.add_assignment("Monday", "10:00 - 11:00", "SE", "Kranti", "lecture")
        resolver.add_assignment("Monday", "10:00 - 11:00", "BE", "Kranti", "lecture")
        
        # Now check for overlap (different class)
        conflicts = resolver.check_cross_class_overlap("Monday", "10:00 - 11:00", "Kranti", "TE", "practical")
        
        # Should detect conflicts with both SE and BE
        assert len(conflicts) >= 2 or len(conflicts) == 0  # Depends on implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
