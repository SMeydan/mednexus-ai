// header.js
class MedHeader extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: "open" });

    const wrapper = document.createElement("header");
    wrapper.innerHTML = `
      <style>
        header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 80px;
          background: radial-gradient(circle at top right, #502a8e, #01020a);
          border-bottom: 0.5px solid #8660ba;
          font-family: 'Inter', sans-serif;
        }

        .logo {
          font-weight: 700;
          font-size: 1.3rem;
          background: linear-gradient(90deg, #00aaff, #8660ba);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          cursor: pointer;
        }

        nav ul {
          list-style: none;
          display: flex;
          gap: 30px;
          margin: 0;
          padding: 0;
        }

        nav a {
          text-decoration: none;
          color: #cfd8e3;
          font-weight: 500;
          cursor: pointer;
        }

        nav a:hover {
          color: #8660ba;
        }

        .btn-outline {
          background-color: transparent;
          color: #76cef9;
          border: 2px solid transparent;
          border-radius: 6px;
          padding: 8px 20px;
          cursor: pointer;
          transition: all 0.3s ease;
          background-image: linear-gradient(#502a8e, #40226fff),
              linear-gradient(90deg, #00aaff, #8660ba);
          background-origin: border-box;
          background-clip: padding-box, border-box;
          font-family: 'Inter', sans-serif;
        }

        .btn-outline:hover {
          color: #fff;
          background-image: linear-gradient(90deg, #00aaff, #8660ba);
          box-shadow: 0 0 15px rgba(134, 96, 186, 0.5);
          transform: translateY(-2px);
        }
      </style>

      <div class="logo">⚕️ MedNexus</div>

      <nav>
        <ul>
          <li><a href="/about">About Team</a></li>
          <li><a href="/report" class="create-report">Create Report</a></li>
          <li><a href="/login-patient" class="btn-outline patient-btn">Patient Login</a></li>
          <li><a href="/login" class="btn-outline auth-btn">Login</a></li>
        </ul>
      </nav>
    `;

    shadow.appendChild(wrapper);
  }

  connectedCallback() {
    window.addEventListener("storage", () => this.updateAuthButtons());
    this.initNavigationOverrides();
    this.updateAuthButtons();
  }

  initNavigationOverrides() {
    const logo = this.shadowRoot.querySelector(".logo");
    logo.addEventListener("click", () => {
      window.location.href = "/";
    });

    // tüm a taglerine override
    this.shadowRoot.querySelectorAll("nav a").forEach(link => {
      const target = link.getAttribute("href");
      link.addEventListener("click", e => {
        e.preventDefault();
        if (target) window.location.href = target;
      });
    });
  }

  updateAuthButtons() {
    const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
    const userType = localStorage.getItem("userType"); // doctor | patient | null

    const authBtn = this.shadowRoot.querySelector(".auth-btn");
    const patientBtn = this.shadowRoot.querySelector(".patient-btn");
    const createReport = this.shadowRoot.querySelector(".create-report");

    const isDoctor = userType === "doctor";
    const isPatient = userType === "patient";

    /* ---------- AUTH BUTTON ---------- */
    if (authBtn) {
      if (isLoggedIn && isDoctor) {
        authBtn.textContent = "Logout";
        authBtn.href = "#";
        authBtn.onclick = e => {
          e.preventDefault();
          this.logout();
        };
      } else if (!isLoggedIn) {
        authBtn.textContent = "Login";
        authBtn.href = "/login";
      } else if (isPatient) {
        // hasta giriş yaptı → doktor login butonu gizle
        authBtn.style.display = "none";
      }
    }

    /* ---------- PATIENT LOGIN BUTTON ---------- */
    if (patientBtn) {
      if (isLoggedIn && isPatient) {
        patientBtn.textContent = "Logout";
        patientBtn.href = "#";
        patientBtn.onclick = e => {
          e.preventDefault();
          this.logout();
        };
      } else if (isDoctor) {
        // doktor giriş yaptı → hasta login gereksiz
        patientBtn.style.display = "none";
      }
    }

    /* ---------- CREATE REPORT BUTTON ---------- */
    if (createReport) {
      if (isPatient) {
        // Hasta → tamamen gizle
        createReport.style.display = "none";
      }
      else if (isDoctor) {
        // Doktor → aktif
        createReport.style.display = "inline-block";
        createReport.href = "/home.html";
      }
      else {
        // Giriş yok → login'e yönlendir
        createReport.style.display = "inline-block";
        createReport.href = "/login.html";
      }
    }
  }

  logout() {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("userType");
    localStorage.removeItem("userToken");
    window.location.href = "/";
  }
}

customElements.define("med-header", MedHeader);
