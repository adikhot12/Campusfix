
import streamlit as st

from agent import analyze_complaint

import streamlit as st

st.markdown(
    """
    <div style="padding:20px; background:#172554; border-radius:15px; text-align:center;">
        <h2 style="color:white;">🌐 Welcome to CampusFix</h2>
        <p style="color:#c7d2fe;">Click below to visit our website</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.link_button(
    "🌐 Open Website",
    "http://127.0.0.1:5500/frontend/index.html",
    use_container_width=True,
)


from database import (
    init_db,
    create_ticket,
    get_tickets,
    get_ticket_events,
    update_status,
    find_reporter_ticket,
)
from tools import CATEGORIES, detect_missing_information

st.set_page_config(
    page_title="CampusFix",
    page_icon="🏫",
    layout="wide",
)

init_db()

st.title("🏫 CampusFix")
st.caption("Offline campus operations and maintenance agent")
st.caption("Local processing only · No API key · No model download")

tickets = get_tickets()

total = len(tickets)
open_count = sum(t["status"] == "Open" for t in tickets)
progress_count = sum(t["status"] == "In Progress" for t in tickets)
resolved_count = sum(t["status"] == "Resolved" for t in tickets)
high_count = sum(t["priority"] == "High" for t in tickets)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Tickets", total)
m2.metric("Open", open_count)
m3.metric("In Progress", progress_count)
m4.metric("Resolved", resolved_count)
m5.metric("High Priority", high_count)

report_tab, dashboard_tab, about_tab = st.tabs(
    ["📝 Report an Issue", "📊 Ticket Dashboard", "ℹ️ How It Works"]
)

with report_tab:
    st.subheader("Report a campus issue")
    st.write(
        "Describe the issue and give its location. "
        "CampusFix will classify it locally and route it to a team."
    )


with st.form("report_issue_form"):
    st.subheader("Report a Campus Issue")

    complaint = st.text_area(
        "Describe your problem",
        placeholder="Example: There is a water problem in the washroom.",
        height=120,
    )

    location = st.text_input(
        "Campus location",
        placeholder="Example: Block B, second-floor washroom",
    )

    contact_name = st.text_input(
        "Your full name",
        max_chars=100,
        placeholder="Enter your name",
    )

    mobile_number = st.text_input(
        "Your mobile number",
        max_chars=16,
        placeholder="Enter your mobile number using digits only",
    )

    submitted = st.form_submit_button(
        "Analyze and Create Ticket",
        type="primary",
        use_container_width=True,
    )

if submitted:
    complaint = complaint.strip()
    location = location.strip()
    contact_name = contact_name.strip()
    mobile_number = mobile_number.strip()

    if not complaint:
        st.error("Please describe the campus problem.")
    elif not location:
        st.error("Please enter the campus location.")
    elif not contact_name:
        st.error("Please enter your name.")
    elif not mobile_number.isdigit() or not (7 <= len(mobile_number) <= 15):
        st.error("Enter a valid mobile number using 7–15 digits.")
    else:
        try:
            with st.spinner("Analyzing your complaint..."):
                analysis = analyze_complaint(
                    complaint,
                    location,
                )

                ticket_id = create_ticket(
                    complaint,
                    analysis,
                    contact_name=contact_name,
                    mobile_number=mobile_number,
                )

            st.success(
                f"Complaint submitted successfully! "
                f"Your ticket number is CF-{ticket_id:04d}"
            )

            st.write("**Issue category:**", analysis["category"])
            st.write("**Priority:**", analysis["priority"])
            st.write("**Assigned team:**", analysis["assigned_team"])
            st.write("**Status:** Open")

            if analysis["priority"] == "High":
                st.error(
                    "🚨 HIGH PRIORITY: This complaint needs prompt staff attention."
                )

            if analysis.get("needs_review"):
                st.warning(
                    "This complaint may need manual review by campus staff."
                )

        except Exception as e:
            st.error(f"Could not create the ticket: {e}")


with dashboard_tab:
    st.subheader("Campus issue tracker")

    tickets = get_tickets()

    if not tickets:
        st.info("No tickets yet. Submit a complaint to get started.")
    else:
        f1, f2, f3 = st.columns(3)

        with f1:
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "Open", "In Progress", "Resolved"],
            )

        with f2:
            priority_filter = st.selectbox(
                "Filter by priority",
                ["All", "High", "Medium", "Low"],
            )

        with f3:
            search_text = st.text_input(
                "Search tickets",
                placeholder="Ticket ID, location, category...",
            ).strip().lower()

        filtered = []
        for ticket in tickets:
            if status_filter != "All" and ticket["status"] != status_filter:
                continue
            if (
                priority_filter != "All"
                and ticket["priority"] != priority_filter
            ):
                continue

            searchable = " ".join([
                str(ticket["id"]),
                ticket["complaint"],
                ticket["category"],
                ticket["location"],
                ticket["assigned_team"],
            ]).lower()

            if search_text and search_text not in searchable:
                continue

            filtered.append(ticket)

        if not filtered:
            st.info("No tickets match these filters.")

        for ticket in filtered:
            ticket_id = ticket["id"]
            public_id = f"CF-{ticket_id:04d}"

            priority_icon = {
                "High": "🔴",
                "Medium": "🟠",
                "Low": "🟢",
            }.get(ticket["priority"], "⚪")

            heading = (
                f"{public_id} · {ticket['category']} · "
                f"{priority_icon} {ticket['priority']} · "
                f"{ticket['status']}"
            )

            with st.expander(heading):
                st.markdown(f"**Complaint:** {ticket['complaint']}")
                st.write(f"📍 Location: {ticket['location']}")
                st.write(f"👥 Assigned team: {ticket['assigned_team']}")
                st.write(f"Workflow step: {ticket['workflow_step']}")
                st.write(f"Created: {ticket['created_at']}")
                st.caption(f"Mode: {ticket['ai_mode']}")

                confidence = float(ticket.get("confidence", 0.5))
                st.write(f"Classification confidence: {confidence:.0%}")

                if ticket.get("needs_review"):
                    st.warning(
                        "This ticket was flagged for classification review."
                    )

                current_status = ticket["status"]
                options = ["Open", "In Progress", "Resolved"]

                selected_status = st.selectbox(
                    "Update ticket status",
                    options,
                    index=options.index(current_status),
                    key=f"status_{ticket_id}",
                )

                if st.button(
                    "Save status",
                    key=f"save_{ticket_id}",
                ):
                    try:
                        update_status(ticket_id, selected_status)
                        st.success("Ticket status updated.")
                        st.rerun()
                    except (ValueError, OSError) as exc:
                        st.error(f"Could not update ticket: {exc}")

                events = get_ticket_events(ticket_id)
                st.markdown("**Workflow history**")

                if events:
                    for event in events:
                        st.write(
                            f"• **{event['event']}** — "
                            f"{event['details']} "
                            f"({event['created_at']})"
                        )
                else:
                    st.caption(
                        "No event history is available for this older ticket."
                    )

with about_tab:
    st.subheader("How CampusFix works")
    st.write(
        "CampusFix is an offline decision-support prototype. "
        "It uses transparent keyword rules rather than a generative AI model."
    )

    st.markdown(
        """
        **Workflow**

        1. **Submit** — collect the complaint and location.
        2. **Triage** — match complaint phrases to a category.
        3. **Prioritize** — detect urgent safety and maintenance terms.
        4. **Assign** — route the ticket to the appropriate team.
        5. **Track** — save events and let staff update the status.
        6. **Review** — flag low-confidence or ambiguous classifications.

        **Limitations**

        - Keyword rules can misunderstand unusual wording.
        - Confidence is a heuristic score, not a trained model probability.
        - High-priority tickets should be verified by campus staff.
        - This prototype does not contact emergency services or dispatch staff.
        """
    )

st.divider()
st.caption(
    "CampusFix Hackathon Prototype · Offline rules · "
    "Validated routing · SQLite persistence"
)
