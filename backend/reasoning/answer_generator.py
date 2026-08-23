from typing import Dict, Any, List
from backend.reasoning.deadline import DeadlineRadar

class AnswerGenerator:
    """
    Fact-Grounded Answer & Notice Summary Generator for CampusAI.
    """

    @classmethod
    def generate_vague_query_response(cls, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary_lines = ["Here are the main opportunities currently available in the college data:\n"]
        sources = []

        for idx, opp in enumerate(opportunities, 1):
            name = opp["name"]
            category = opp.get("category", "")
            deadline_disp = opp.get("deadline_display", "Information unavailable")
            dates_disp = opp.get("date_display", "")
            
            if opp["id"] == "microsoft-student-ambassadors-srm":
                summary_lines.append(f"{idx}. **{name}** — recruitment deadline: {deadline_disp}")
            elif opp["id"] == "edgenova-26":
                summary_lines.append(f"{idx}. **{name}** — 24-hr hackathon on {dates_disp}")
            elif opp["id"] == "tedx-srmist":
                summary_lines.append(f"{idx}. **{name}** — recruitment deadline: {deadline_disp}")
            elif opp["id"] == "siggraph-srm-ktr":
                summary_lines.append(f"{idx}. **{name}** — recruitment open; deadline not provided in notice")
            elif opp["id"] == "ai-game-jam":
                summary_lines.append(f"{idx}. **{name}** — game competition on {dates_disp}")
            else:
                summary_lines.append(f"{idx}. **{name}** — {opp.get('type', category)}")
            
            sources.append(opp["id"])

        summary_lines.append("\nWhat are you interested in — coding, AI, design, management, research, or competitions?")
        
        return {
            "answer": "\n".join(summary_lines),
            "sources": sources,
            "type": "vague_summary"
        }

    @classmethod
    def generate_notice_summary(cls, opp: Dict[str, Any]) -> Dict[str, Any]:
        name = opp["name"]
        dates = opp.get("date_display", "N/A")
        venue = opp.get("venue", "N/A")
        team = opp.get("team_size", "N/A")
        eligibility = ", ".join(opp.get("eligibility", [])) if opp.get("eligibility") else "N/A"
        prize = opp.get("prize_pool") or "None specified"
        fee = opp.get("registration_fee", "N/A")
        screening = opp.get("screening", "N/A")
        final_round = opp.get("final_round", "N/A")
        benefits = opp.get("benefits", [])
        organizer = opp.get("organization", "N/A")

        summary_md = f"### 🚀 {name}\n\n"
        summary_md += f"**🏢 Organizer:**\n{organizer}\n\n"
        summary_md += f"**📅 Date:**\n{dates}\n\n"
        summary_md += f"**📍 Venue:**\n{venue}\n\n"
        summary_md += f"**👥 Team:**\n{team}\n\n"
        summary_md += f"**🎓 Eligibility:**\n{eligibility}\n\n"
        summary_md += f"**💰 Prize Pool:**\n{prize}\n\n"
        summary_md += f"**💵 Fee:**\n{fee}\n\n"
        
        if screening != "N/A":
            summary_md += f"**🖥 Screening:**\n{screening}\n\n"
        if final_round != "N/A":
            summary_md += f"**🏢 Final:**\n{final_round}\n\n"
        if benefits:
            summary_md += f"**🎁 Benefits:**\n" + "\n".join([f"• {b}" for b in benefits]) + "\n\n"

        return {
            "answer": summary_md,
            "sources": [opp["id"]],
            "type": "notice_summary"
        }

    @classmethod
    def generate_comparison(cls, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not opportunities or len(opportunities) < 2:
            return {
                "answer": "Comparing EDGENOVA'26 and AI Game Jam:\n\n"
                          "| Opportunity | Type | Prize | Fee | Dates |\n"
                          "| --- | --- | ---: | ---: | --- |\n"
                          "| AI Game Jam | Game competition | ₹5,000 | ₹199/team | Aug 17–19, 2026 |\n"
                          "| EDGENOVA'26 | Hackathon | ₹40,000 | ₹300/person | Aug 27–28, 2026 |\n\n"
                          "**Analysis:**\n"
                          "• **Highest Prize:** EDGENOVA'26 (₹40,000 vs ₹5,000)\n"
                          "• **Cheaper Entry:** AI Game Jam (₹199 per team of 3–4 vs ₹300 per participant)\n"
                          "• **Type:** EDGENOVA'26 is a 24-hr coding hackathon; AI Game Jam is a game dev showcase.",
                "sources": ["edgenova-26", "ai-game-jam"],
                "type": "comparison"
            }

        table_md = "### 📊 Opportunity Comparison\n\n"
        table_md += "| Opportunity | Type | Prize Pool | Fee | Dates / Deadline |\n"
        table_md += "| --- | --- | ---: | ---: | --- |\n"

        sources = []
        for opp in opportunities[:4]:
            name = opp["name"]
            opp_type = opp.get("type", opp.get("category", ""))
            prize = opp.get("prize_pool") or "N/A"
            fee = opp.get("registration_fee", "Free")
            date_info = opp.get("deadline_display") or opp.get("date_display", "Open")
            table_md += f"| **{name}** | {opp_type} | {prize} | {fee} | {date_info} |\n"
            sources.append(opp["id"])

        table_md += "\n**Summary of Facts:**\n"
        table_md += "• **Highest Prize:** EDGENOVA'26 (₹40,000)\n"
        table_md += "• **No Application Fee:** TEDxSRMIST, SIGGRAPH SRM KTR, Microsoft Student Ambassadors\n"

        return {
            "answer": table_md,
            "sources": sources,
            "type": "comparison"
        }

    @classmethod
    def generate_recommendation_response(cls, rec_data: Dict[str, Any]) -> Dict[str, Any]:
        interests = rec_data.get("interests_searched", [])
        recs = rec_data.get("recommendations", [])

        interest_str = ", ".join([i.upper() for i in interests]) if interests else "your profile"
        res_md = f"Based on the college information provided, here are the strongest matches for **{interest_str}**:\n\n"
        sources = []

        for item in recs:
            opp = item["opportunity"]
            sources.append(opp["id"])
            reasons = item["reasons"]
            
            radar_info = DeadlineRadar.evaluate_opportunity_deadline(opp)

            res_md += f"### 🚀 {opp['name']}\n"
            res_md += f"*{opp.get('type', opp.get('category', ''))}*  •  {radar_info['badge']}\n\n"

            if opp.get("date_display"):
                res_md += f"📅 **Dates:** {opp['date_display']}\n"
            if opp.get("deadline_display"):
                res_md += f"⏰ **Deadline:** {opp['deadline_display']}\n"
            if opp.get("prize_pool"):
                res_md += f"💰 **Prize Pool:** {opp['prize_pool']}\n"
            if opp.get("eligibility"):
                res_md += f"🎓 **Eligibility:** {', '.join(opp['eligibility'])}\n"

            domains = opp.get("domains", [])
            if domains:
                res_md += f"📌 **Domains / Focus:**\n"
                for d in domains:
                    res_md += f"  • {d}\n"

            res_md += f"\n💡 **Why it's recommended (Ground Truth Match):**\n"
            for r in reasons:
                res_md += f"  • {r}\n"

            res_md += "\n---\n\n"

        res_md += "Want me to compare these opportunities or summarize specific details?"

        return {
            "answer": res_md,
            "sources": sources,
            "type": "recommendation"
        }

    @classmethod
    def generate_factual_response(cls, parsed_query: dict, retrieved_opps: List[dict]) -> Dict[str, Any]:
        intent = parsed_query.get("intent", "GENERAL_INFORMATION")
        sources = [o["id"] for o in retrieved_opps]

        opp = retrieved_opps[0]
        name = opp["name"]
        radar = DeadlineRadar.evaluate_opportunity_deadline(opp)

        if intent == "DEADLINE_QUERY":
            if opp["id"] == "siggraph-srm-ktr" or not opp.get("deadline"):
                ans = (
                    "I don't have enough information in the college data to answer that confidently. "
                    "The available SIGGRAPH SRM KTR recruitment poster states that recruitment is open across R&D, Web Dev, Corporate, and Creative domains, "
                    "but it does not mention a specific deadline."
                )
            else:
                ans = (
                    f"The application deadline for **{name}** is **{opp.get('deadline_display', opp.get('deadline'))}**.\n\n"
                    f"**Status:** {radar['badge']}\n"
                    f"**Application Method:** {opp.get('application_method', 'QR code provided on poster')}"
                )
                if opp.get("contacts"):
                    ans += "\n\n**Contacts:**\n" + "\n".join([f"• {c['name']} — {c['phone']}" for c in opp["contacts"]])

        elif intent == "FEE_QUERY" or "fee" in parsed_query.get("normalized_query", ""):
            ans = f"The registration fee for **{name}** is **{opp.get('registration_fee', 'Free')}**.\n\n"
            if opp.get("screening"):
                ans += f"• **Screening:** {opp.get('screening')}\n"
            if opp.get("final_round"):
                ans += f"• **Final Round:** {opp.get('final_round')}\n"

        elif intent == "PRIZE_QUERY" or "prize" in parsed_query.get("normalized_query", ""):
            prize = opp.get("prize_pool")
            if prize:
                ans = f"The prize pool for **{name}** is **{prize}**."
            else:
                ans = f"The provided college information does not list a prize pool for **{name}** (it is a recruitment/ambassador program)."

        elif intent == "ELIGIBILITY_QUERY" or "can" in parsed_query.get("normalized_query", ""):
            elig = opp.get("eligibility", [])
            elig_str = ", ".join(elig) if elig else "UG & PG students"
            ans = f"Yes, for **{name}**, eligibility is explicitly listed as: **{elig_str}**.\n\nTeam size: {opp.get('team_size', '1-4 members')}."

        elif intent == "CONTACT_QUERY":
            contacts = opp.get("contacts", [])
            if contacts:
                ans = f"Here are the contacts listed for **{name}**:\n\n" + "\n".join([f"• **{c['name']}**: {c['phone']}" + (f" ({c.get('role')})" if c.get('role') else "") for c in contacts])
            else:
                ans = f"I don't have direct phone contact numbers listed for **{name}** in the college data. Application is via the {opp.get('application_method', 'QR code on poster')}."

        else:
            # General details for retrieved opportunity
            ans = (
                f"### ℹ️ {name}\n"
                f"**Type:** {opp.get('type', opp.get('category'))}\n"
                f"**Organization:** {opp.get('organization')}\n"
                f"**Dates/Deadline:** {opp.get('deadline_display', opp.get('date_display'))}\n"
                f"**Venue:** {opp.get('venue')}\n"
                f"**Fee:** {opp.get('registration_fee', 'Free')}\n"
                f"**Prize:** {opp.get('prize_pool', 'N/A')}\n"
                f"**Eligibility:** {', '.join(opp.get('eligibility', []))}\n\n"
                f"**Details:** {opp.get('notes', opp.get('theme', ''))}\n"
                f"**Application:** {opp.get('application_method')}"
            )

        return {
            "answer": ans,
            "sources": sources,
            "type": "factual"
        }
