import axios from "axios";

const API_ROOT = "http://127.0.0.1:8000";

const MARKET_TREND_ENDPOINT = `${API_ROOT}/api/chat/market-trends/analyse/`;
const SUBURB_PDF_ENDPOINT = `${API_ROOT}/api/chat/suburb-stats/pie-charts/`;
const AMENITY_SCORE_ENDPOINT = `${API_ROOT}/api/chat/amenity-score/`;

const REGISTER_ENDPOINT = `${API_ROOT}/api/users/register/`;
const LOGIN_ENDPOINT = `${API_ROOT}/api/users/login/`;
const LOGOUT_ENDPOINT = `${API_ROOT}/api/users/logout/`;
const ME_ENDPOINT = `${API_ROOT}/api/users/me/`;

function getAuthHeaders() {
    const token = localStorage.getItem("authToken");

    if (!token) {
        return {};
    }

    return {
        Authorization: `Token ${token}`,
    };
}

export async function registerUser(formData) {
    const response = await axios.post(REGISTER_ENDPOINT, formData);
    return response.data;
}

export async function loginUser(formData) {
    const response = await axios.post(LOGIN_ENDPOINT, formData);
    return response.data;
}

export async function logoutUser() {
    const response = await axios.post(
        LOGOUT_ENDPOINT,
        {},
        {
            headers: getAuthHeaders(),
        }
    );

    return response.data;
}

export async function getCurrentUser() {
    const response = await axios.get(ME_ENDPOINT, {
        headers: getAuthHeaders(),
    });

    return response.data;
}

export async function getAmenityScore(address) {
    const response = await axios.post(
        AMENITY_SCORE_ENDPOINT,
        {
            address: address,
        },
        {
            headers: getAuthHeaders(),
        }
    );

    return response.data;
}

export async function uploadMarketTrendPdf(file) {
    const formData = new FormData();
    formData.append("pdf", file);

    const response = await axios.post(MARKET_TREND_ENDPOINT, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
            ...getAuthHeaders(),
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
            ...getAuthHeaders(),
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