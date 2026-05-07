import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/chat";

export async function createChatSession(title = "New Chat") {
    const response = await axios.post(`${API_BASE_URL}/sessions/`, {
        title,
    });

    return response.data;
}

export async function sendMessage(sessionId, content) {
    const response = await axios.post(
        `${API_BASE_URL}/sessions/${sessionId}/messages/`,
        {
            content,
        }
    );

    return response.data;
}

export async function getMessages(sessionId) {
    const response = await axios.get(
        `${API_BASE_URL}/sessions/${sessionId}/messages/`
    );

    return response.data;
}