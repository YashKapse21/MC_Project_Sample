import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy import sympify, latex, integrate, symbols, lambdify

# --- PAGE CONFIG ---
st.set_page_config(page_title="Double Integral Step-Grader", layout="wide")

# --- INITIALIZE SESSION STATE ---
def init_state(reset_all=False):
    if reset_all:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    if 'marks' not in st.session_state:
        st.session_state.marks = 10.0
    if 'hints_used' not in st.session_state:
        st.session_state.hints_used = 0
    if 'step1_correct' not in st.session_state:
        st.session_state.step1_correct = False

init_state()
x, y = symbols('x y')

# --- TOP ROW: TITLE & SCOREBOARD ---
head_col, score_col = st.columns([2.5, 1.5])

with head_col:
    st.title("🔢 Double Integral Step-Grader")

with score_col:
    # Display Score and Hint Count
    st.info(f"**Marks:** {st.session_state.marks}/10  |  **Hints Used:** {st.session_state.hints_used}/2")
    
    # Nested columns to put buttons side-by-side
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("🔄 Reset All", use_container_width=True):
            init_state(reset_all=True)
            st.rerun()
            
    with btn_col2:
        if st.session_state.hints_used < 2:
            if st.button("💡 Use Hint", use_container_width=True):
                st.session_state.hints_used += 1
                st.session_state.marks -= 2.5
                st.rerun()
        else:
            st.button("💡 Max Hints", disabled=True, use_container_width=True)

# --- MAIN LAYOUT ---
col_in, col_graph = st.columns([1, 1.2])

with col_in:
    st.subheader("1. Problem Setup")
    f_text = st.text_input("Function f(x, y):", "x*y", key="f_in")
    y_low = st.text_input("y Lower Limit", "0", key="yl")
    y_high = st.text_input("y Upper Limit", "x", key="yh")
    x_low = st.text_input("x Lower Limit", "0", key="xl")
    x_high = st.text_input("x Upper Limit", "1", key="xh")

# --- MATH BACK-END ---
try:
    f_sym = sympify(f_text)
    inner_truth = integrate(f_sym, (y, sympify(y_low), sympify(y_high)))
    outer_truth = integrate(inner_truth, (x, sympify(x_low), sympify(x_high)))

    with col_graph:
        st.subheader("2. Surface Visualization")
        f_num = lambdify((x, y), f_sym, "numpy")
        x_r = np.linspace(float(sympify(x_low)), float(sympify(x_high)), 30)
        y_r = np.linspace(0, 2, 30)
        X, Y = np.meshgrid(x_r, y_r)
        Z = f_num(X, Y)
        fig = plt.figure(figsize=(5, 3.5))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        st.pyplot(fig)

    st.divider()

    # --- HINT DISPLAY AREA ---
    if st.session_state.hints_used >= 1:
        st.warning(f"**Hint 1 (Inner Result):** ${latex(inner_truth)}$")
    if st.session_state.hints_used >= 2:
        st.warning(f"**Hint 2 (Final Result):** ${latex(outer_truth)}$")

    # --- STEP 1: INNER INTEGRAL ---
    st.subheader("Step 1: Solve the Inner Integral")
    st.latex(rf"\int_{{{y_low}}}^{{{y_high}}} {latex(f_sym)} \,dy")
    
    ans_step1 = st.text_input("Your result for Step 1:", key="ans1")
    if st.button("Check Step 1"):
        if (sympify(ans_step1) - inner_truth).evalf() == 0:
            st.session_state.step1_correct = True
            st.success("Step 1 Correct!")
        else:
            st.error("Incorrect. Try again or use a hint.")

    # --- STEP 2: OUTER INTEGRAL ---
    if st.session_state.step1_correct:
        st.divider()
        st.subheader("Step 2: Solve the Outer Integral")
        st.latex(rf"\int_{{{x_low}}}^{{{x_high}}} ({latex(inner_truth)}) \,dx")
        
        ans_step2 = st.text_input("Your final result:", key="ans2")
        if st.button("Submit Final Answer"):
            if (sympify(ans_step2) - outer_truth).evalf() == 0:
                st.success(f"Perfect! You've completed the problem with {st.session_state.marks} marks.")
                st.balloons()
            else:
                st.error("Final answer is incorrect.")

except Exception as e:
    st.info("Please enter valid mathematical inputs to start.")
