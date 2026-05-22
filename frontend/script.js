const newsGrid = document.getElementById("newsGrid");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const pageInfo = document.getElementById("pageInfo");

let currentPage = 1;
const size = 12;
let totalPages = 1;

const logos = {
    "OpenAI": "https://images.squarespace-cdn.com/content/v1/62ec2bc76a27db7b37a2b32f/685e2b49-ff29-423e-8f35-dbcbe521566e/ai-companies-openai.jpg?format=2500w",
    "LangChain": "https://avatars.githubusercontent.com/u/126733545?s=200&v=4",
    "Hugging Face": "https://huggingface.co/front/assets/huggingface_logo.svg",
    "arXiv AI": "https://static.arxiv.org/static/base/1.0.1/images/arxiv-logo-one-color-white.svg",
    "arXiv ML": "https://static.arxiv.org/static/base/1.0.1/images/arxiv-logo-one-color-white.svg",
    "arXiv NLP": "https://static.arxiv.org/static/base/1.0.1/images/arxiv-logo-one-color-white.svg",
    "Google News AI": "https://www.gstatic.com/images/branding/product/1x/googleg_48dp.png"
};

async function loadNews(page = 1) {
    const response = await fetch(`/all-article?page=${page}&size=${size}`);
    const data = await response.json();

    console.log("API DATA:", data);

    const articles = data.items;

    if (!articles || articles.length === 0) {
        newsGrid.innerHTML = `<h2>No articles found.</h2>`;
        return;
    }

    currentPage = data.page;
    totalPages = data.pages;

    newsGrid.innerHTML = "";

    articles.forEach(article => {
        const logo = logos[article.source] || "https://www.gstatic.com/images/branding/product/1x/googleg_48dp.png";

        const card = document.createElement("div");
        card.className = "news-card";

        card.innerHTML = `
            <div class="card-header">
                <div class="provider">
                    <img src="${logo}" alt="${article.source || "source"}">
                    <div>
                        <h3>${article.source || "Unknown"}</h3>
                        <span>${article.published_at || "No Date"}</span>
                    </div>
                </div>
            </div>

            <div class="card-body">
                <h2>${article.title || "No Title"}</h2>
                <p>${article.summary || "No summary available."}</p>
            </div>

            <div class="card-footer">
                <a href="${article.url}" target="_blank">Read Article →</a>
            </div>
        `;

        newsGrid.appendChild(card);
    });

    pageInfo.innerText = `Page ${currentPage} of ${totalPages}`;

    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
}

prevBtn.addEventListener("click", () => {
    if (currentPage > 1) {
        loadNews(currentPage - 1);
    }
});

nextBtn.addEventListener("click", () => {
    if (currentPage < totalPages) {
        loadNews(currentPage + 1);
    }
});

loadNews();