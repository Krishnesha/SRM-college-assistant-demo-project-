from datetime import datetime, date
from typing import Dict, Any, List

class DeadlineRadar:
    """
    Deadline Awareness & Radar Logic for CampusAI.
    Base reference date: 19 August 2026 (or system current date).
    """

    REFERENCE_DATE = date(2026, 8, 19)

    @classmethod
    def parse_iso_date(cls, date_str: str) -> date:
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    @classmethod
    def evaluate_opportunity_deadline(cls, opp: Dict[str, Any], current_date: date = None) -> Dict[str, Any]:
        if current_date is None:
            current_date = cls.REFERENCE_DATE

        deadline_str = opp.get("deadline")
        dates_list = opp.get("dates", [])
        name = opp.get("name", "")

        if not deadline_str and not dates_list:
            return {
                "id": opp["id"],
                "name": name,
                "status": "UNAVAILABLE",
                "badge": "⚪ Deadline unavailable",
                "color": "gray",
                "days_left": None,
                "label": "Deadline not specified in college data"
            }

        # Check end date for multi-day events like AI Game Jam (Aug 17-19)
        end_date = cls.parse_iso_date(dates_list[-1]) if dates_list else cls.parse_iso_date(deadline_str) if deadline_str else None

        if not end_date:
            return {
                "id": opp["id"],
                "name": name,
                "status": "UNAVAILABLE",
                "badge": "⚪ Deadline unavailable",
                "color": "gray",
                "days_left": None,
                "label": "Deadline not specified in college data"
            }

        delta_days = (end_date - current_date).days

        if delta_days < 0:
            return {
                "id": opp["id"],
                "name": name,
                "status": "EXPIRED",
                "badge": "🔴 Closed",
                "color": "red",
                "days_left": delta_days,
                "label": f"Ended {abs(delta_days)} days ago"
            }
        elif delta_days == 0:
            return {
                "id": opp["id"],
                "name": name,
                "status": "TODAY",
                "badge": "🔴 Ending today",
                "color": "red",
                "days_left": 0,
                "label": "Happening / Ending today!"
            }
        elif delta_days <= 3:
            return {
                "id": opp["id"],
                "name": name,
                "status": "SOON",
                "badge": f"🟠 Due in {delta_days} day{'s' if delta_days > 1 else ''}",
                "color": "orange",
                "days_left": delta_days,
                "label": f"Deadline soon: {opp.get('deadline_display', '')}"
            }
        else:
            return {
                "id": opp["id"],
                "name": name,
                "status": "UPCOMING",
                "badge": f"🟢 Upcoming ({delta_days} days)",
                "color": "green",
                "days_left": delta_days,
                "label": f"Upcoming: {opp.get('deadline_display', opp.get('date_display'))}"
            }

    @classmethod
    def get_radar_summary(cls, opportunities: List[Dict[str, Any]], current_date: date = None) -> List[Dict[str, Any]]:
        summary = []
        for opp in opportunities:
            eval_res = cls.evaluate_opportunity_deadline(opp, current_date)
            summary.append({
                **opp,
                "radar": eval_res
            })
        return summary
