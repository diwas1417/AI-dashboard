import axios from "axios";

const API_ROOT = "http://127.0.0.1:8000";

const MARKET_TREND_ENDPOINT = `${API_ROOT}/api/chat/market-trends/analyse/`;
const SUBURB_PDF_ENDPOINT = `${API_ROOT}/api/chat/suburb-stats/pie-charts/`;

export async function uploadMarketTrendPdf(file) {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await axios.post(MARKET_TREND_ENDPOINT, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    return response.data;
}

export async function uploadSuburbPdf(file) {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await axios.post(SUBURB_PDF_ENDPOINT, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    return response.data;
}

export function getFullMediaUrl(url) {
    if (!url) return "";

    if (url.startsWith("http://") || url.startsWith("https://")) {
        return url;
    }

    if (url.startsWith("/")) {
        return `${API_ROOT}${url}`;
    }

    return `${API_ROOT}/${url}`;
}