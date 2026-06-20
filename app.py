import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API = "http://127.0.0.1:8000"

# ====================================================
# PAGE CONFIG
# ====================================================

st.set_page_config(
    page_title="Employee Leave Management",
    page_icon="🏢",
    layout="wide"
)

# ====================================================
# CSS
# ====================================================

st.markdown("""
<style>

/* Background Image */

.stApp{
    background:
    linear-gradient(
        rgba(0,0,0,0.45),
        rgba(0,0,0,0.45)
    ),
    url("https://images.unsplash.com/photo-1672009190560-12e7bade8d09?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

/* Glass Card */

.glass-card{
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);

    border: 1px solid rgba(255,255,255,0.15);

    border-radius: 25px;

    padding: 35px;

    box-shadow:
    0 8px 32px rgba(0,0,0,0.35);
}

/* Headings */

h1,h2,h3,h4,h5,h6{
    color:white !important;
}

/* Labels */

label{
    color:white !important;
    font-weight:600 !important;
}

/* Input Fields */

.stTextInput input,
.stTextArea textarea{

    background:
    rgba(255,255,255,0.9) !important;

    color:black !important;

    border-radius:12px !important;
}

/* Selectbox */

div[data-baseweb="select"]{
    background:white !important;
    border-radius:12px !important;
}

div[data-baseweb="select"] *{
    color:black !important;
}

/* Buttons */

.stButton button{

    width:100%;

    height:50px;

    border:none;

    border-radius:30px;

    background:
    linear-gradient(
        90deg,
        #7c3aed,
        #9333ea
    );

    color:white !important;

    font-size:18px;

    font-weight:bold;
}

/* Sidebar */

[data-testid="stSidebar"]{
    background:
    rgba(15,23,42,0.8);

    backdrop-filter: blur(15px);
}

[data-testid="stSidebar"] *{
    color:white !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* Login Card */

.login-card{
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);

    border: 1px solid rgba(255,255,255,0.18);

    border-radius: 28px;

    padding: 15px;

    box-shadow:
    0 8px 32px rgba(0,0,0,0.35);
}

/* Center title */

.login-title{
    text-align:center;
    color:white;
    font-size:35px;
    font-weight:700;
    margin-bottom:5px;
}

.login-subtitle{
    text-align:center;
    color:white;
    opacity:0.9;
    margin-bottom:20px;
}

/* Footer */

.login-footer{
    text-align:center;
    color:white;
    opacity:0.8;
    margin-top:15px;
    font-size:14px;
}
/* Force inner tab text white */
button[data-baseweb="tab"] p{
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ====================================================
# SESSION
# ====================================================

if "user" not in st.session_state:
    st.session_state.user = None

# ====================================================
# LOGIN SCREEN
# ====================================================

if st.session_state.user is None:

    left, center, right = st.columns([1, 1.3, 1])

    with center:

        st.markdown("""
        <div class="login-wrapper">
            <div class="login-card">
                <div class="login-title">
                    ⚡TeamPulse⚡
                </div>
                <div class="login-subtitle">
                Smart Leave & Workforce Management
                </div>    
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        role = st.radio("Login As", ["Employee", "Manager", "Admin"],horizontal=True)

        email = st.text_input(
            "Email Address",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "Login",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{API}/login",
                    json={
                        "email": email,
                        "password": password
                    }
                )

                result = response.json()
                if result["success"]:

                  if result["role"].lower() == role.lower():
                    st.session_state.user = result
                    st.rerun()

                  else:

                    st.error(
                       f"Selected role is '{role.title()}' but this account belongs to '{result['role'].title()}'.")

                else:

                  st.error("Invalid Email or Password")

            except Exception:

                st.error(
                    "Backend server is not running."
                )

        st.markdown("""
        <div class="login-footer">
        Developed by Dhivyaa Premkumar | 2026
        </div>
        """, unsafe_allow_html=True)
# ====================================================
# DASHBOARDS
# ====================================================

else:

    user = st.session_state.user

    with st.sidebar:

        st.markdown(f"""
        <div style="
        background:rgba(255,255,255,0.1);
        padding:15px;
        border-radius:12px;
        margin-bottom:10px;
        color:white;
        ">
        👤 <b>{user['name']}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
        background:rgba(59,130,246,0.2);
        padding:15px;
        border-radius:12px;
        color:white;
        ">
        🏷️ <b>{user['role'].title()}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "Logout",
            use_container_width=True
        ):
            st.session_state.user = None
            st.rerun()

    # ====================================================
    # EMPLOYEE
    # ====================================================

    if user["role"] == "employee":

        st.title("Employee Dashboard")

        balance = requests.get(
            f"{API}/leave_balance/{user['id']}"
        ).json()

        c1, c2, c3 = st.columns(3)

        with c1:
          st.markdown(f"""
          <div class="glass-card">
          <h4 style="color:white;">Casual Leave</h4>
          <h1 style="color:white;">{balance['casual']}</h1>
          </div>
          """, unsafe_allow_html=True)

        with c2:
          st.markdown(f"""
          <div class="glass-card">
          <h4 style="color:white;">Sick Leave</h4>
          <h1 style="color:white;">{balance['sick']}</h1>
          </div>
          """, unsafe_allow_html=True)

        with c3:
          st.markdown(f"""
          <div class="glass-card">
          <h4 style="color:white;">Earned Leave</h4>
          <h1 style="color:white;">{balance['earned']}</h1>
          </div>
          """, unsafe_allow_html=True)

        st.divider()

        st.subheader("Apply Leave")

        leave_type = st.selectbox(
            "Leave Type",
            [
                "Casual",
                "Sick",
                "Earned"
            ]
        )

        start = st.date_input("Start Date")

        end = st.date_input("End Date")

        days = st.number_input(
            "Number of Days",
            min_value=1,
            value=1
        )

        reason = st.text_area(
            "Reason"
        )

        if st.button("Apply Leave"):

            response = requests.post(
                f"{API}/apply_leave",
                json={
                    "employee_id": user["id"],
                    "leave_type": leave_type,
                    "start_date": str(start),
                    "end_date": str(end),
                    "days": days,
                    "reason": reason
                }
            )

            result = response.json()

            if result["success"]:
                st.success(
                    result["message"]
                )
            else:
                st.error(
                    result["message"]
                )

        st.divider()

        st.subheader("Leave History")

        history = requests.get(
            f"{API}/leave_history/{user['id']}"
        ).json()

        if history:

            df = pd.DataFrame(
                history,
                columns=[
                    "ID",
                    "Type",
                    "Start",
                    "End",
                    "Days",
                    "Reason",
                    "Status",
                    "Applied On"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            chart = df["Status"].value_counts()

            fig = px.pie(
                values=chart.values,
                names=chart.index,
                title="Leave Status Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # ====================================================
    # MANAGER
    # ====================================================
    elif user["role"] == "manager":

    # =========================
    # DASHBOARD HEADER
    # =========================
     st.title("Manager Dashboard")
    requests_list = requests.get(
        f"{API}/manager_requests/{user['id']}"
    ).json()

    if requests_list:

        df = pd.DataFrame(
            requests_list,
            columns=[
                "Leave ID",
                "Employee",
                "Leave Type",
                "Start",
                "End",
                "Days",
                "Reason",
                "Status"
            ]
        )

        # =========================
        # SUMMARY CARDS
        # =========================

        pending_count = (
            df["Status"] == "Pending"
        ).sum()

        approved_count = (
            df["Status"] == "Approved"
        ).sum()

        total_requests = len(df)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
              <div class="glass-card">
                <h5 style="color:white;text-align:center;">
                     Pending Requests
                </h5>

                <h1 style="
                color:white;
                text-align:center;
                ">
                    {pending_count}
                </h1>
               </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
              <div class="glass-card">
                <h5 style="color:white;text-align:center;">
                       Approved 
                </h5>
                <h1 style="
                color:white;
                text-align:center;
                ">
                    {approved_count}
                </h1>
               </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
              <div class="glass-card">
                <h5 style="color:white;text-align:center;">
                     Total Requests
                </h5>

                <h1 style="
                color:white;
                text-align:center;
                ">
                    {total_requests}
                </h1>
               </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # LEAVE REQUESTS TABLE
        # =========================
        st.subheader("📋Employee Leave Requests")
        st.dataframe(
            df,
            use_container_width=True
        )

        # =========================
        # ANALYTICS CHART
        # =========================
        st.subheader("📊 Leave Analytics")
        fig = px.bar(
            df,
            x="Employee",
            y="Days",
            color="Status",
            title="Employee Leave Requests"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =========================
        # APPROVAL CENTER
        # =========================
        st.subheader("⚡ Leave Approval Center")

        leave_id = st.number_input(
            "Leave ID",
            min_value=1,
            value=1
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✅ Approve",
                use_container_width=True
            ):

                requests.put(
                    f"{API}/approve/{leave_id}/{user['id']}"
                )

                st.success(
                    "Leave Approved Successfully"
                )

                st.rerun()

        with col2:

            if st.button(
                "❌ Reject",
                use_container_width=True
            ):

                requests.put(
                    f"{API}/reject/{leave_id}/{user['id']}"
                )

                st.error(
                    "Leave Rejected"
                )

                st.rerun()

            else:
             st.info("No Leave Requests to Approve or Reject")
             
    # ====================================================
    # ADMIN
    # ====================================================

    elif user["role"] == "admin":

        st.title("Admin Dashboard")

        stats = requests.get(
            f"{API}/stats"
        ).json()

        c1, c2, c3, c4, c5 = st.columns(5)

        card_style = """
         height:120px;
         display:flex;
         flex-direction:column;
         justify-content:center;
         align-items:center;
         text-align:center;"""

        with c1:
         st.markdown(f"""
            <div class="glass-card" style="{card_style}">
              <h6 style="color:white;margin:0;white-space:nowrap;">
                 👥 Employees
              </h6>
              <h2 style="color:white;margin:5px 0 0 0;">
              {stats["employees"]}
              </h2>
            </div>
    """, unsafe_allow_html=True)

        with c2:
         st.markdown(f"""
             <div class="glass-card" style="{card_style}">
               <h6 style="color:white;margin:0;white-space:nowrap;">
                  👨‍💼 Managers
               </h6>
               <h2 style="color:white;margin:5px 0 0 0;">
               {stats["managers"]}
               </h2>
             </div>
    """, unsafe_allow_html=True)

        with c3:
         st.markdown(f"""
              <div class="glass-card" style="{card_style}">
                 <h6 style="color:white;margin:0;white-space:nowrap;">
                   ⏳ Pending
                 </h6>
                 <h2 style="color:white;margin:5px 0 0 0;">
                 {stats["pending"]}
                 </h2>
                 </div>
    """, unsafe_allow_html=True)

        with c4:
          st.markdown(f"""
               <div class="glass-card" style="{card_style}">
                   <h6 style="color:white;margin:0;white-space:nowrap;">
                     ✅ Approved
                   </h6>
                   <h2 style="color:white;margin:5px 0 0 0;">
                    {stats["approved"]}
                   </h2>
                </div>
    """, unsafe_allow_html=True)

        with c5:
          st.markdown(f"""
              <div class="glass-card" style="{card_style}">
                 <h6 style="color:white;margin:0;white-space:nowrap;">
                   ❌ Rejected
                 </h6>
                 <h2 style="color:white;margin:5px 0 0 0;">
                  {stats["rejected"]}
                 </h2>
             </div>
    """, unsafe_allow_html=True)
        st.subheader("📊 Leave Statistics")
        chart_df = pd.DataFrame({
            "Status":[
                "Pending",
                "Approved",
                "Rejected"
            ],
            "Count":[
                stats["pending"],
                stats["approved"],
                stats["rejected"]
            ]
        })

        fig = px.pie(
            chart_df,
            values="Count",
            names="Status",
            title="Leave Statistics"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        tab1, tab2, tab3 = st.tabs(
            [
                "Create Employee",
                "Create Manager",
                "Reports"
            ]
        )

        # =====================================
        # CREATE EMPLOYEE
        # =====================================

        with tab1:

            managers = requests.get(
                f"{API}/managers"
            ).json()

            manager_dict = {}

            for m in managers:
                manager_dict[m[1]] = m[0]

            name = st.text_input(
                "Employee Name"
            )

            email = st.text_input(
                "Employee Email"
            )

            password = st.text_input(
                "Employee Password"
            )

            selected_manager = st.selectbox(
                "Manager",
                list(manager_dict.keys())
            )

            if st.button("Create Employee"):

                requests.post(
                    f"{API}/create_employee",
                    json={
                        "name": name,
                        "email": email,
                        "password": password,
                        "manager_id":
                        manager_dict[selected_manager]
                    }
                )

                st.success(
                    "Employee Created"
                )

        # =====================================
        # CREATE MANAGER
        # =====================================

        with tab2:

            manager_name = st.text_input(
                "Manager Name"
            )

            manager_email = st.text_input(
                "Manager Email"
            )

            manager_password = st.text_input(
                "Manager Password"
            )
            if st.button("Create Manager"):
              response = requests.post(f"{API}/create_manager",json={"name": manager_name,"email": manager_email,"password": manager_password}
    )

              #st.write(response.status_code)
              #st.write(response.text)
            #if st.button(
              #  "Create Manager"
            #):

                #requests.post(
                    #f"{API}/create_manager",
                    #json={
                        #"name": manager_name,
                        #"email": manager_email,
                        #"password": manager_password
                   # }
                #)

            st.success(
                    "Manager Created"
                )

        # =====================================
        # REPORTS
        # =====================================

        with tab3:

            st.subheader("All Users")

            users = requests.get(
                f"{API}/users"
            ).json()

            if users:

                users_df = pd.DataFrame(
                    users,
                    columns=[
                        "ID",
                        "Name",
                        "Email",
                        "Role",
                        "Manager ID"
                    ]
                )

                st.dataframe(
                    users_df,
                    use_container_width=True
                )

            st.subheader(
                "All Leave Requests"
            )

            leaves = requests.get(
                f"{API}/all_leaves"
            ).json()

            if leaves:

                leave_df = pd.DataFrame(
                    leaves,
                    columns=[
                        "ID",
                        "Employee",
                        "Type",
                        "Start",
                        "End",
                        "Days",
                        "Status"
                    ]
                )

                st.dataframe(
                    leave_df,
                    use_container_width=True
                )