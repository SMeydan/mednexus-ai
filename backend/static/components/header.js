// header.js
class MedHeader extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: "open" });

    const wrapper = document.createElement("header");
    wrapper.innerHTML = `
      <style>
        /* 1. HEADER ALANI */
        header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 80px;
          
          /* Arka Plan: Beyaz Buzlu Cam Efekti */
          background: rgba(255, 255, 255, 0.85); 
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          
          /* Alt Çizgi: Teal renginin çok silik hali */
          border-bottom: 1px solid rgba(50, 135, 146, 0.15);
          
          font-family: 'Inter', sans-serif;
          position: sticky;
          top: 0;
          z-index: 1000;
          transition: all 0.3s ease;
        }

        /* 2. LOGO */
        .logo {
          font-weight: 800;
          font-size: 1.5rem;
          /* Logo rengi: Teal -> Koyu Teal Gradyan */
          background: linear-gradient(90deg, #328792, #1d5f66);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          cursor: pointer;
          letter-spacing: -0.5px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        /* 3. MENÜ LİNKLERİ */
        nav ul {
          list-style: none;
          display: flex;
          align-items: center;
          gap: 30px;
          margin: 0;
          padding: 0;
        }

        nav a {
          text-decoration: none;
          color: #555; /* Koyu gri (okunabilirlik için) */
          font-weight: 500;
          cursor: pointer;
          transition: color 0.3s ease;
          font-size: 0.95rem;
        }

        nav a:hover {
          color: #328792; /* Hoverda ana Teal rengi */
        }

        /* "Create Report" linki için özel vurgu (opsiyonel) */
        nav a.create-report {
           font-weight: 600;
        }

        /* 4. BUTONLAR (Outline Stil) */
        .btn-outline {
          background-color: transparent;
          color: #328792; /* Yazı rengi Teal */
          border: 2px solid transparent;
          border-radius: 10px;
          padding: 8px 20px;
          cursor: pointer;
          transition: all 0.3s ease;
          font-weight: 600;
          text-decoration: none;
          display: inline-block;

          /* Kenarlık Gradyanı Hilesi */
          background-image: linear-gradient(#ffffff, #ffffff),
              linear-gradient(90deg, #5dcbd6, #328792);
          background-origin: border-box;
          background-clip: padding-box, border-box;
          
          box-shadow: 0 4px 10px rgba(50, 135, 146, 0.05);
        }

        .btn-outline:hover {
          color: #fff;
          /* Hoverda zemin tamamen Teal gradyan */
          background-image: linear-gradient(90deg, #5dcbd6, #328792);
          box-shadow: 0 4px 15px rgba(50, 135, 146, 0.3);
          transform: translateY(-2px);
          border: 2px solid transparent;
        }

        /* MOBİL UYUMU */
        @media (max-width: 860px) {
            header {
                padding: 15px 20px;
            }
            nav ul {
                display: none; /* Basit gizleme (hamburger menü eklenebilir) */
            }
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

    // SPA benzeri geçişler için linkleri yakala
    this.shadowRoot.querySelectorAll("nav a").forEach(link => {
      const target = link.getAttribute("href");
      // Eğer href="#" ise veya link boşsa yönlendirme yapma
      if (target && target !== "#") {
        link.addEventListener("click", e => {
           // Burada tam sayfa yenilemesi mi yoksa SPA mantığı mı istediğine göre
           // e.preventDefault() kullanabilirsin. 
           // Şimdilik standart davranış (sayfa yenileme) için dokunmuyorum 
           // veya senin kodundaki mantığı koruyorum:
           
           /* Eğer tamamen SPA (Single Page App) ise:
           e.preventDefault();
           window.history.pushState({}, "", target);
           // ...router logic...
           */
        });
      }
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

    /* ---------- AUTH BUTTON (Doktor Login) ---------- */
    if (authBtn) {
      if (isLoggedIn && isDoctor) {
        authBtn.textContent = "Logout";
        authBtn.href = "#";
        // Logout butonuna basınca outline stili korunsun ama belki renk değişsin istersen buraya style ekleyebilirsin
        authBtn.onclick = e => {
          e.preventDefault();
          this.logout();
        };
      } else if (!isLoggedIn) {
        authBtn.textContent = "Login";
        authBtn.href = "/login";
        authBtn.style.display = "inline-block";
      } else if (isPatient) {
        // Hasta giriş yaptıysa Doktor login butonunu gizle
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
        // Doktor giriş yaptıysa Hasta login butonunu gizle
        patientBtn.style.display = "none";
      } else {
        // Kimse girmediyse göster
        patientBtn.style.display = "inline-block";
      }
    }

    /* ---------- CREATE REPORT BUTTON (Sadece Doktor) ---------- */
    if (createReport) {
      if (isDoctor) {
        createReport.parentElement.style.display = "block"; // Li'yi göster
        createReport.href = "/home.html";
      } else {
        // Hasta ise veya giriş yapılmadıysa gizle
        createReport.parentElement.style.display = "none"; 
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