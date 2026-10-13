"""Shared upper-edge datum prototype; does not yet rebuild CAD geometry.
All lengths are millimeters. Board pose remains a provisional measured envelope.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class UpperEdge:
    tray_upper_y_mm: float = 17.5923586623637
    cap_inner_wall_y_mm: float = 17.5923586623637
    pcb_upper_y_mm: float = 17.4
    pcb_seat_x_mm: float = 5.28706399647303
    pcb_thickness_mm: float = 0.25
    tray_upper_edge_offset_mm: float = 0.0
    catch_overlap_mm: float = 0.4
    catch_gap_above_seat_mm: float = 0.6

    def datums(self):
        if not 0 <= self.tray_upper_edge_offset_mm <= 1.0:
            raise ValueError('Exploratory range is 0 to 1 mm; not a validated CAD range')
        if self.catch_gap_above_seat_mm < self.pcb_thickness_mm:
            raise ValueError('Catch would squeeze the nominal board')
        # Case dimensions follow the offset. Electronics and capture remain fixed.
        upper = self.tray_upper_y_mm + self.tray_upper_edge_offset_mm
        cap = self.cap_inner_wall_y_mm + self.tray_upper_edge_offset_mm
        return {
            'tray_upper_y_mm': upper,
            'cap_inner_wall_y_mm': cap,
            'pcb_upper_y_mm': self.pcb_upper_y_mm,
            'catch_inner_tip_y_mm': self.pcb_upper_y_mm - self.catch_overlap_mm,
            'catch_underside_x_mm': self.pcb_seat_x_mm + self.catch_gap_above_seat_mm,
            'side_room_to_cap_wall_mm': cap - self.pcb_upper_y_mm,
            'board_lift_clearance_mm': self.catch_gap_above_seat_mm - self.pcb_thickness_mm,
        }
