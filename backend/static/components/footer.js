class MedFooter extends HTMLElement {
    constructor() {
        super();

        // Shadow DOM oluşturuyoruz (izole stil ve içerik)
        const shadow = this.attachShadow({ mode: "open" });

        // Template
        const wrapper = document.createElement("footer");
        wrapper.innerHTML = `
            <style>
                footer {
                    text-align: center;
                    padding: 20px;
                    background: rgba(50, 135, 146, 0.15);
                    font-size: 0.9rem;
                    color: #8892a5;
                }
            </style>
            © 2025 MedNexus - Written with ♥ by Team HexaMind
        `;

        shadow.appendChild(wrapper);
    }
}
customElements.define("med-footer", MedFooter);
