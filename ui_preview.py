
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="CampusFix | Campus Operations",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- DESIGN SYSTEM ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #f5f7fc;
    color: #17223b;
}
[data-testid="stSidebar"] {
    background: #111b35;
    border-right: 1px solid #24304e;
}
[data-testid="stSidebar"] * { color: #e5eaf7; }
.brand {
    font-size: 27px; font-weight: 800; letter-spacing: -1px;
    color: white; padding: 12px 0 2px;
}
.brand span { color: #8295ff; }
.side-caption {
    color: #8290ad; font-size: 11px; letter-spacing: 2px;
    font-weight: 700; margin: 26px 0 10px;
}
.side-note {
    background: #1b2847; border: 1px solid #344363;
    border-radius: 14px; padding: 15px; margin-top: 28px;
    color: #dce5ff; font-size: 13px; line-height: 1.6;
}
.eyebrow {
    text-transform: uppercase; letter-spacing: 2px;
    color: #6c7ca0; font-size: 11px; font-weight: 800;
}
.page-title {
    font-size: 34px; font-weight: 800; letter-spacing: -1.4px;
    color: #17223b; line-height: 1.15; margin: 5px 0;
}
.subtitle { color: #77839c; font-size: 14px; }
.hero {
    background: linear-gradient(115deg, #18284f 0%, #354ac0 62%, #6478f3 100%);
    border-radius: 22px; padding: 28px 30px; color: white;
    margin: 12px 0 24px;
}
.hero h2 { color: white; font-size: 25px; margin: 5px 0 8px; }
.hero p { color: #e1e7ff; font-size: 14px; }
.hero-label {
    color: #c7d1ff; text-transform: uppercase;
    letter-spacing: 2px; font-size: 10px; font-weight: 800;
}
.metric {
    background: white; border: 1px solid #e7ebf4;
    border-radius: 16px; padding: 18px 18px 16px;
    min-height: 130px; box-shadow: 0 3px 15px #19284c08;
}
.metric-label { color: #75819a; font-size: 12px; font-weight: 600; }
.metric-value { font-size: 32px; color: #182441; font-weight: 800; margin: 8px 0 3px; }
.metric-foot { color: #75819a; font-size: 11px; }
.section-title { font-size: 19px; font-weight: 800; color: #1b2742; }
.section-sub { color: #8490a7; font-size: 12px; }
.panel {
    background: white; border: 1px solid #e7ebf4;
    border-radius: 18px; padding: 20px; margin-bottom: 15px;
}
.ticket {
    background: white; border: 1px solid #e7ebf4;
    border-radius: 15px; padding: 17px 18px; margin: 10px 0;
}
.ticket-title { font-size: 15px; font-weight: 800; color: #202c48; }
.ticket-meta { font-size: 12px; color: #7c88a0; margin-top: 5px; }
.pill {
    display: inline-block; border-radius: 7px; padding: 4px 8px;
    font-size: 10px; font-weight: 800; letter-spacing: .4px;
}
.high { background: #fff0ee; color: #c93d36; }
.medium { background: #fff5df; color: #a56b00; }
.low { background: #e7f8ef; color: #218052; }
.status { background: #edf1ff; color: #4a5dc0; }
.small-heading { font-size: 13px; font-weight: 800; color: #283551; }
.activity { border-left: 2px solid #e1e7f3; padding: 1px 0 15px 14px; margin-left: 5px; }
.activity:last-child { border-left-color: transparent; }
.activity-title { font-size: 12px; font-weight: 700; color: #35415d; }
.activity-meta { font-size: 11px; color: #8490a7; margin-top: 3px; }
div.stButton > button[kind="primary"] {
    background: #4d61dc; border: 0; border-radius: 10px;
    min-height: 44px; font-weight: 700;
}
div.stButton > button {
    border-radius: 9px; font-weight: 600;
}
div[data-testid="stForm"] {
    background: white; border: 1px solid #e6eaf3;
    border-radius: 18px; padding: 22px;
}
hr { border-color: #e7ebf4; }
#MainMenu, footer { visibility: hidden; }
@media (max-width: 768px) {
    .page-title { font-size: 27px; }
    .hero { padding: 20px; }
}
</style>
""", unsafe_allow_html=True)


# ---------- DEMO DATA ----------
if "preview_tickets" not in st.session_state:
    st.session_state.preview_tickets = [
        {
            "id": "CF-0104",
            "issue": "Power failure in Science Lab",
            "location": "Block C · 2nd Floor",
            "category": "Electrical",
            "priority": "High",
            "status": "Open",
            "team": "Electrical Maintenance",
            "reporter": "Demo User",
            "mobile": "0000000000",
        },
        {
            "id": "CF-0103",
            "issue": "Water problem in washroom",
            "location": "Hostel Block B",
            "category": "Plumbing",
            "priority": "High",
            "status": "In Progress",
            "team": "Plumbing and Water Facilities",
            "reporter": "Demo User",
            "mobile": "0000000000",
        },
        {
            "id": "CF-0102",
            "issue": "Wi-Fi unavailable",
            "location": "Central Library · Level 1",
            "category": "IT",
            "priority": "Medium",
            "status": "In Progress",
            "team": "IT Support",
            "reporter": "Demo User",
            "mobile": "0000000000",
        },
        {
            "id": "CF-0101",
            "issue": "Classroom projector not working",
            "location": "Academic Block A · Room 204",
            "category": "Classroom",
            "priority": "Low",
            "status": "Resolved",
            "team": "Classroom Maintenance",
            "reporter": "Demo User",
            "mobile": "0000000000",
        },
    ]

tickets = st.session_state.preview_tickets


# ---------- HELPERS ----------
def section_heading(title, subtitle=""):
    st.markdown(f"""
    <div class="section-title">{title}</div>
    <div class="section-sub">{subtitle}</div>
    """, unsafe_allow_html=True)


def ticket_card(t):
    priority_class = t["priority"].lower()
    status_class = "status"
    st.markdown(f"""
    <div class="ticket">
      <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap">
        <div class="ticket-title">{t['issue']}</div>
        <div>
          <span class="pill {priority_class}">{t['priority'].upper()} PRIORITY</span>
          <span class="pill {status_class}">{t['status'].upper()}</span>
        </div>
      </div>
      <div class="ticket-meta">{t['id']} &nbsp;·&nbsp; {t['location']}</div>
      <div class="ticket-meta">Assigned team: {t['team']}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(
        '<div class="brand">Campus<span>Fix</span> ✦</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#8794b3;font-size:12px;">CAMPUS OPERATIONS PLATFORM</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-caption">WORKSPACE</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Overview", "Report an Issue", "Track Tickets", "Operations"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="side-caption">SYSTEM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:13px;color:#c4cee5;">● Offline demo mode</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div class="side-note">
      <b>✦ CampusFix Assistant</b><br>
      Turn campus problems into organized, trackable service requests.
      <br><br>
      <span style="color:#9eafff">● Local preview</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#72809f;font-size:11px;margin-top:25px;">CAMPUSFIX PREVIEW · V1.0</div>',
        unsafe_allow_html=True,
    )


# ---------- OVERVIEW ----------
if page == "Overview":
    high_count = sum(
        1 for t in tickets
        if t["priority"] == "High" and t["status"] != "Resolved"
    )
    open_count = sum(1 for t in tickets if t["status"] == "Open")
    progress_count = sum(1 for t in tickets if t["status"] == "In Progress")
    resolved_count = sum(1 for t in tickets if t["status"] == "Resolved")

    left, right = st.columns([3, 1])
    with left:
        st.markdown('<div class="eyebrow">OVERVIEW / CAMPUS HEALTH</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-title">Campus Operations</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subtitle">One workspace for a better-running campus.</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f'<div style="text-align:right;color:#8290a7;font-size:12px;padding-top:14px;">'
            f'{datetime.now().strftime("%A, %d %B %Y")}<br>Offline preview</div>',
            unsafe_allow_html=True,
        )

    st.markdown("""
    <div class="hero">
      <div class="hero-label">✦ YOUR CAMPUS, UNDER CONTROL</div>
      <h2>Small issues. Smarter solutions.</h2>
      <p>Report a problem, route it to the right team, and follow every ticket through resolution.</p>
    </div>
    """, unsafe_allow_html=True)

    metrics = [
        ("TOTAL TICKETS", len(tickets), "All demo requests"),
        ("HIGH PRIORITY", high_count, "Needs prompt attention"),
        ("IN PROGRESS", progress_count, "Being worked on"),
        ("RESOLVED", resolved_count, "Completed demo requests"),
    ]
    cols = st.columns(4)
    for col, (label, value, foot) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric">
              <div class="metric-label">{label}</div>
              <div class="metric-value">{value:02d}</div>
              <div class="metric-foot">{foot}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    left_col, right_col = st.columns([1.55, 1], gap="large")

    with left_col:
        section_heading("Priority incidents", "Issues that may need attention first")
        active = sorted(
            [t for t in tickets if t["status"] != "Resolved"],
            key=lambda t: {"High": 0, "Medium": 1, "Low": 2}.get(t["priority"], 3),
        )
        if active:
            for t in active:
                ticket_card(t)
        else:
            st.success("No active incidents in this preview.")

    with right_col:
        section_heading("Ticket distribution", "Live from this preview's demo data")
        counts = {}
        for t in tickets:
            counts[t["category"]] = counts.get(t["category"], 0) + 1
        for category, count in sorted(counts.items(), key=lambda x: -x[1]):
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:13px 0;border-bottom:1px solid #edf0f6;">'
                f'<span style="font-size:13px;color:#53617c;">{category}</span>'
                f'<b style="font-size:13px;color:#263451;">{count}</b></div>',
                unsafe_allow_html=True,
            )

        st.write("")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        section_heading("Recent activity", "A quick look at ticket movement")
        for title, meta in [
            ("Ticket CF-0104 submitted", "Electrical · Science Lab"),
            ("Ticket CF-0103 assigned", "Plumbing and Water Facilities"),
            ("Ticket CF-0101 resolved", "Classroom Maintenance"),
        ]:
            st.markdown(f"""
            <div class="activity">
              <div class="activity-title">{title}</div>
              <div class="activity-meta">{meta}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Preview notice: the dashboard above uses sample data stored only in this browser session.")


# ---------- REPORT AN ISSUE ----------
elif page == "Report an Issue":
    st.markdown('<div class="eyebrow">SERVICE DESK / NEW REQUEST</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Report an issue</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Tell us what is wrong. We’ll organize the request for the right team.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    info, form_col = st.columns([0.85, 1.5], gap="large")
    with info:
        st.markdown("""
        <div class="panel">
          <div style="font-size:32px">🛠️</div>
          <div class="section-title">How it works</div>
          <br>
          <b>01 · Describe</b><br>
          <span class="section-sub">Tell us what happened and where.</span><br><br>
          <b>02 · Triage</b><br>
          <span class="section-sub">Review the category and urgency.</span><br><br>
          <b>03 · Track</b><br>
          <span class="section-sub">Keep the ticket number to check progress.</span>
        </div>
        <div class="panel">
          <div class="small-heading">🚨 Safety first</div>
          <div class="section-sub">For fire, electric shock, gas leaks or immediate danger, contact campus security or local emergency services immediately. Do not wait for this demo form.</div>
        </div>
        """, unsafe_allow_html=True)

    with form_col:
        with st.form("preview_report_form", clear_on_submit=True):
            st.markdown("### Request details")
            name = st.text_input("Your name", placeholder="Enter your full name")
            mobile = st.text_input("Mobile number", placeholder="Digits only")
            location = st.text_input(
                "Campus location",
                placeholder="e.g. Block B, second-floor washroom",
            )
            category = st.selectbox(
                "Issue category",
                ["IT", "Plumbing", "Electrical", "Classroom", "Cleaning",
                 "Safety", "Pest Control", "Other"],
            )
            priority = st.selectbox(
                "How urgent is it?",
                ["Medium", "Low", "High"],
                index=0,
            )
            description = st.text_area(
                "Describe the issue",
                placeholder="What happened? Include details that help the team locate the issue.",
                height=140,
            )
            submit = st.form_submit_button(
                "＋ Create preview ticket",
                type="primary",
                use_container_width=True,
            )

        if submit:
            if not name.strip() or not location.strip() or not description.strip():
                st.error("Please complete your name, location and issue description.")
            elif not mobile.strip().isdigit() or not 7 <= len(mobile.strip()) <= 15:
                st.error("Please enter a mobile number with 7–15 digits.")
            else:
                new_number = 105
                existing_ids = []
                for item in tickets:
                    try:
                        existing_ids.append(int(item["id"].split("-")[1]))
                    except (ValueError, IndexError):
                        pass
                if existing_ids:
                    new_number = max(existing_ids) + 1

                ticket = {
                    "id": f"CF-{new_number:04d}",
                    "issue": description.strip(),
                    "location": location.strip(),
                    "category": category,
                    "priority": priority,
                    "status": "Open",
                    "team": {
                        "IT": "IT Support",
                        "Plumbing": "Plumbing and Water Facilities",
                        "Electrical": "Electrical Maintenance",
                        "Classroom": "Classroom Maintenance",
                        "Cleaning": "Housekeeping",
                        "Safety": "Campus Safety and Security",
                        "Pest Control": "Pest Control",
                        "Other": "General Campus Support",
                    }[category],
                    "reporter": name.strip(),
                    "mobile": mobile.strip(),
                }
                st.session_state.preview_tickets.insert(0, ticket)
                st.success(f"Preview ticket created: {ticket['id']}")
                st.info("This ticket exists only in the preview session. It is not saved to your CampusFix SQLite database.")


# ---------- TRACK TICKETS ----------
elif page == "Track Tickets":
    st.markdown('<div class="eyebrow">SERVICE DESK / TRACKING</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Track your tickets</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Look up a request and see its latest preview status.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    ticket_ids = [t["id"] for t in tickets]
    with st.form("preview_track_form"):
        chosen_id = st.selectbox("Ticket number", ticket_ids if ticket_ids else ["No tickets"])
        mobile = st.text_input("Mobile number", placeholder="Enter the number used in the preview form")
        track = st.form_submit_button("Find my ticket", type="primary")

    if track:
        match = next(
            (
                t for t in tickets
                if t["id"] == chosen_id and t["mobile"] == mobile.strip()
            ),
            None,
        )
        if match:
            st.markdown(f"""
            <div class="panel">
              <div class="eyebrow">{match['id']}</div>
              <div class="section-title">{match['issue']}</div>
              <p class="section-sub">{match['location']}</p>
              <span class="pill {match['priority'].lower()}">{match['priority'].upper()} PRIORITY</span>
              <span class="pill status">{match['status'].upper()}</span>
              <hr>
              <b>Assigned team:</b> {match['team']}<br><br>
              <b>Category:</b> {match['category']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Ticket and mobile number do not match. For sample tickets, use mobile number 0000000000.")

    section_heading("All preview tickets", "Demo data for exploring the interface")
    for t in tickets:
        ticket_card(t)


# ---------- OPERATIONS ----------
elif page == "Operations":
    st.markdown('<div class="eyebrow">OPERATIONS / TEAM WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Operations center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Review sample incidents and try status updates in the preview.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    for t in sorted(
        tickets,
        key=lambda x: {"High": 0, "Medium": 1, "Low": 2}.get(x["priority"], 3),
    ):
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**{t['id']} · {t['issue']}**")
                st.caption(f"{t['location']} · {t['team']}")
                st.caption(f"Priority: {t['priority']} · Reported by: {t['reporter']}")
            with c2:
                options = ["Open", "In Progress", "Resolved"]
                current = t["status"]
                new_status = st.selectbox(
                    "Update status",
                    options,
                    index=options.index(current),
                    key=f"status_{t['id']}",
                )
                if st.button("Save status", key=f"save_{t['id']}"):
                    for item in st.session_state.preview_tickets:
                        if item["id"] == t["id"]:
                            item["status"] = new_status
                    st.success(f"{t['id']} updated to {new_status}.")
                    st.rerun()

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#8994aa;font-size:11px;">'
    'CAMPUSFIX · OFFLINE UI PREVIEW · SAMPLE DATA ONLY'
    '</div>',
    unsafe_allow_html=True,
)
