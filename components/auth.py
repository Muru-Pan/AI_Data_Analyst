import streamlit as st
from core.auth import create_user, verify_user

def render_auth():
    with open("assets/auth_style.css", "r") as f:
        css = f.read()
    st.markdown(f"<link href='https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;800;900&display=swap' rel='stylesheet'><style>{css}</style>", unsafe_allow_html=True)

    login_tab, sign_tab = st.tabs(["Sign In", "Register"])

    with login_tab:
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<div class="login-title">Login</div>', unsafe_allow_html=True)
            l_user = st.text_input("u", placeholder="Email ID", label_visibility="collapsed")
            l_pass = st.text_input("p", type="password", placeholder="Password", label_visibility="collapsed")
            st.markdown('<div class="lp-forgot">Forgot Password?</div>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Login", width='stretch')
            st.markdown('<div class="lp-register">Don\'t have an account? <strong>Register</strong></div>', unsafe_allow_html=True)
            if submitted:
                if not l_user or not l_pass:
                    st.error("Please fill in both fields.")
                elif verify_user(l_user, l_pass):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = l_user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with sign_tab:
        with st.form("signup_form", clear_on_submit=True):
            st.markdown('<div class="login-title">Create Account</div>', unsafe_allow_html=True)
            s_user  = st.text_input("un", placeholder="Username", label_visibility="collapsed")
            s_pass  = st.text_input("pw", type="password", placeholder="Password", label_visibility="collapsed")
            s_pass2 = st.text_input("pw2", type="password", placeholder="Confirm Password", label_visibility="collapsed")
            reg_sub = st.form_submit_button("Create Account", width='stretch')
            if reg_sub:
                if s_pass != s_pass2:
                    st.error("Passwords do not match.")
                elif len(s_user) < 3 or len(s_pass) < 5:
                    st.error("Username >=3 chars and password >=5 chars required.")
                else:
                    ok, msg = create_user(s_user, s_pass)
                    if ok:
                        st.success("Account created! Switch to Sign In.")
                    else:
                        st.error(msg)

    st.stop()
