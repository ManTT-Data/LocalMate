/**
 * LocalMate Chatbot - Frontend JavaScript with Plan Integration
 * Connects to /api/v1/chat and /api/v1/planner backends
 */

// API Configuration
const API_BASE = 'http://localhost:8000/api/v1';
const CONFIG = {
    provider: 'MegaLLM',
    model: 'deepseek-ai/deepseek-v3.1-terminus',
    userId: 'test',
    sessionId: 'default'
};

// State
let selectedImageUrl = null;
let selectedImageFile = null;
let isLoading = false;
let currentPlanId = null;
let planItems = [];
let reactMode = false;  // ReAct multi-step mode

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeImage = document.getElementById('removeImage');
const clearBtn = document.getElementById('clearBtn');
const reactToggle = document.getElementById('reactToggle');

// Plan DOM Elements
const planItemsEl = document.getElementById('planItems');
const planEmpty = document.getElementById('planEmpty');
const planCount = document.getElementById('planCount');
const planSummary = document.getElementById('planSummary');
const totalDistance = document.getElementById('totalDistance');
const totalDuration = document.getElementById('totalDuration');
const optimizeBtn = document.getElementById('optimizeBtn');
const clearPlanBtn = document.getElementById('clearPlanBtn');
const optimizeResult = document.getElementById('optimizeResult');
const savedDistance = document.getElementById('savedDistance');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Auto-resize textarea
    messageInput.addEventListener('input', autoResize);

    // Send on Enter
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    imageInput.addEventListener('change', handleImageUpload);
    removeImage.addEventListener('click', clearImage);
    clearBtn.addEventListener('click', clearHistory);
    optimizeBtn.addEventListener('click', optimizeRoute);
    clearPlanBtn.addEventListener('click', clearPlan);
    reactToggle.addEventListener('click', toggleReactMode);

    // Paste image support (Ctrl+V)
    messageInput.addEventListener('paste', handlePaste);
    document.addEventListener('paste', handlePaste);

    // Focus input
    messageInput.focus();

    // Initialize plan
    await initPlan();
});

// Toggle ReAct mode
function toggleReactMode() {
    reactMode = !reactMode;
    reactToggle.textContent = reactMode ? '🧠 ReAct: ON' : '🧠 ReAct: OFF';
    reactToggle.classList.toggle('active', reactMode);
    console.log('ReAct mode:', reactMode ? 'ON' : 'OFF');
}

// Handle paste event for images
function handlePaste(e) {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (const item of items) {
        if (item.type.startsWith('image/')) {
            e.preventDefault();

            const file = item.getAsFile();
            if (!file) continue;

            if (file.size > 10 * 1024 * 1024) {
                alert('File ảnh quá lớn (tối đa 10MB)');
                return;
            }

            // Show preview
            const url = URL.createObjectURL(file);
            previewImg.src = url;
            imagePreview.style.display = 'inline-block';
            selectedImageUrl = url;
            selectedImageFile = file;

            console.log('📷 Image pasted:', file.name || 'clipboard-image');
            return;
        }
    }
}

// ===== Chat Functions =====

function autoResize() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 100) + 'px';
}

function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Vui lòng chọn file ảnh!');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        alert('File ảnh quá lớn (tối đa 10MB)');
        return;
    }

    const url = URL.createObjectURL(file);
    previewImg.src = url;
    imagePreview.style.display = 'inline-block';
    selectedImageUrl = url;
    selectedImageFile = file;
}

function clearImage() {
    imageInput.value = '';
    imagePreview.style.display = 'none';
    previewImg.src = '';
    selectedImageUrl = null;
    selectedImageFile = null;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message && !selectedImageUrl) return;
    if (isLoading) return;

    addMessage('user', message, selectedImageUrl);

    messageInput.value = '';
    messageInput.style.height = 'auto';
    const imageToSend = selectedImageFile;
    clearImage();

    isLoading = true;
    sendBtn.disabled = true;
    const loadingEl = addLoadingMessage();

    try {
        let response;

        if (imageToSend) {
            const base64 = await fileToBase64(imageToSend);
            response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message || 'Tìm địa điểm tương tự ảnh này',
                    user_id: CONFIG.userId,
                    session_id: CONFIG.sessionId,
                    image_url: base64,
                    provider: CONFIG.provider,
                    model: CONFIG.model,
                    react_mode: reactMode
                })
            });
        } else {
            response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    user_id: CONFIG.userId,
                    session_id: CONFIG.sessionId,
                    provider: CONFIG.provider,
                    model: CONFIG.model,
                    react_mode: reactMode
                })
            });
        }

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        loadingEl.remove();

        // Parse response for places (mock for now - AI would return structured data)
        const places = extractPlacesFromResponse(data.response);
        addMessageWithPlaces('assistant', data.response, places);

    } catch (error) {
        console.error('Error:', error);
        loadingEl.remove();
        addMessage('assistant', `❌ Lỗi kết nối: ${error.message}`);
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function addMessage(role, content, imageUrl = null) {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const avatar = role === 'user' ? '👤' : '🤖';
    let imageHtml = imageUrl ? `<img src="${imageUrl}" class="user-image" alt="Uploaded">` : '';
    const formattedContent = formatMessage(content);

    div.innerHTML = `
        <div class="avatar">${avatar}</div>
        <div class="content">
            ${formattedContent}
            ${imageHtml}
        </div>
    `;

    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
}

function addMessageWithPlaces(role, content, places = []) {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const formattedContent = formatMessage(content);

    let placesHtml = '';
    if (places.length > 0) {
        placesHtml = '<div class="place-cards">';
        for (const place of places) {
            const isAdded = planItems.some(p => p.place_id === place.place_id);
            placesHtml += `
                <div class="place-card" data-place='${JSON.stringify(place)}'>
                    <div class="place-info">
                        <div class="place-name">${place.name}</div>
                        <div class="place-meta">
                            ${place.category || ''}
                            ${place.rating ? `<span class="place-rating">★ ${place.rating}</span>` : ''}
                        </div>
                    </div>
                    <button class="add-to-plan-btn ${isAdded ? 'added' : ''}" 
                            onclick="addToPlan(this)" 
                            ${isAdded ? 'disabled' : ''}>
                        ${isAdded ? '✓ Đã thêm' : '+ Add'}
                    </button>
                </div>
            `;
        }
        placesHtml += '</div>';
    }

    div.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="content">
            ${formattedContent}
            ${placesHtml}
        </div>
    `;

    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
}

// Extract places from AI response (simplified parsing)
function extractPlacesFromResponse(text) {
    const places = [];

    // Pattern: **Name** or [Name] with rating
    const patterns = [
        /\*\*([^*]+)\*\*[^★]*★?\s*([\d.]+)?/g,
        /\[([^\]]+)\][^★]*★?\s*([\d.]+)?/g,
    ];

    // Also try to find Vietnamese place patterns
    const lines = text.split('\n');
    for (const line of lines) {
        // Match patterns like: - **Tên quán** - 4.5★
        const match = line.match(/\*\*([^*]+)\*\*/);
        if (match) {
            const name = match[1].trim();
            const ratingMatch = line.match(/([\d.]+)\s*[★⭐]/);
            const rating = ratingMatch ? parseFloat(ratingMatch[1]) : null;

            // Skip generic titles
            if (name.length > 3 && !name.includes(':') && !name.toLowerCase().includes('top')) {
                places.push({
                    place_id: name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, ''),
                    name: name,
                    category: '',
                    rating: rating,
                    lat: 16.06 + Math.random() * 0.05,  // Mock coordinates
                    lng: 108.22 + Math.random() * 0.05
                });
            }
        }
    }

    // Dedupe by name
    const seen = new Set();
    return places.filter(p => {
        if (seen.has(p.name)) return false;
        seen.add(p.name);
        return true;
    }).slice(0, 5);
}

function formatMessage(text) {
    if (!text) return '';
    text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    const paragraphs = text.split('\n\n');
    if (paragraphs.length > 1) {
        text = paragraphs.map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');
    } else {
        text = `<p>${text.replace(/\n/g, '<br>')}</p>`;
    }
    return text;
}

function addLoadingMessage() {
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="content">
            <div class="loading"><span></span><span></span><span></span></div>
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function clearHistory() {
    if (!confirm('Xóa toàn bộ lịch sử chat?')) return;

    try {
        await fetch(`${API_BASE}/chat/clear`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: CONFIG.userId, session_id: CONFIG.sessionId })
        });
    } catch (e) { }

    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach((msg, i) => { if (i > 0) msg.remove(); });
}

// ===== Plan Functions =====

async function initPlan() {
    try {
        // Get or create plan
        const response = await fetch(`${API_BASE}/planner/create?user_id=${CONFIG.userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'My Da Nang Trip' })
        });

        if (response.ok) {
            const data = await response.json();
            currentPlanId = data.plan_id;
            console.log('Plan initialized:', currentPlanId);
        }
    } catch (e) {
        console.log('Could not init plan:', e);
    }

    updatePlanUI();
}

async function addToPlan(btn) {
    const card = btn.closest('.place-card');
    const place = JSON.parse(card.dataset.place);

    if (!currentPlanId) await initPlan();

    btn.disabled = true;
    btn.textContent = '...';

    try {
        const response = await fetch(`${API_BASE}/planner/${currentPlanId}/add?user_id=${CONFIG.userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ place: place })
        });

        if (response.ok) {
            const item = await response.json();
            planItems.push({
                ...item,
                place_id: place.place_id
            });

            btn.textContent = '✓ Đã thêm';
            btn.classList.add('added');

            updatePlanUI();
        } else {
            btn.disabled = false;
            btn.textContent = '+ Add';
        }
    } catch (e) {
        console.error('Add to plan error:', e);
        btn.disabled = false;
        btn.textContent = '+ Add';
    }
}

async function removeFromPlan(itemId) {
    try {
        await fetch(`${API_BASE}/planner/${currentPlanId}/remove/${itemId}?user_id=${CONFIG.userId}`, {
            method: 'DELETE'
        });

        planItems = planItems.filter(p => p.item_id !== itemId);
        updatePlanUI();

        // Re-enable add buttons for this place
        resetAddButtons();
    } catch (e) {
        console.error('Remove error:', e);
    }
}

function resetAddButtons() {
    document.querySelectorAll('.add-to-plan-btn.added').forEach(btn => {
        const card = btn.closest('.place-card');
        if (card) {
            const place = JSON.parse(card.dataset.place);
            const stillInPlan = planItems.some(p => p.place_id === place.place_id);
            if (!stillInPlan) {
                btn.classList.remove('added');
                btn.disabled = false;
                btn.textContent = '+ Add';
            }
        }
    });
}

async function optimizeRoute() {
    if (planItems.length < 2) return;

    optimizeBtn.disabled = true;
    optimizeBtn.textContent = 'Đang tối ưu...';

    try {
        const response = await fetch(`${API_BASE}/planner/${currentPlanId}/optimize?user_id=${CONFIG.userId}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            planItems = data.items;

            // Show saved distance
            if (data.distance_saved_km && data.distance_saved_km > 0) {
                savedDistance.textContent = data.distance_saved_km.toFixed(1);
                optimizeResult.style.display = 'block';

                setTimeout(() => {
                    optimizeResult.style.display = 'none';
                }, 5000);
            }

            updatePlanUI();
        }
    } catch (e) {
        console.error('Optimize error:', e);
    } finally {
        optimizeBtn.disabled = planItems.length < 2;
        optimizeBtn.textContent = '🔀 Tối ưu lộ trình';
    }
}

async function clearPlan() {
    if (!confirm('Xóa toàn bộ plan?')) return;

    try {
        await fetch(`${API_BASE}/planner/${currentPlanId}?user_id=${CONFIG.userId}`, {
            method: 'DELETE'
        });

        planItems = [];
        currentPlanId = null;
        await initPlan();
        resetAddButtons();
    } catch (e) {
        console.error('Clear plan error:', e);
    }
}

function updatePlanUI() {
    // Update count
    planCount.textContent = `${planItems.length} places`;

    // Update optimize button
    optimizeBtn.disabled = planItems.length < 2;

    // Show/hide empty state
    if (planItems.length === 0) {
        planEmpty.style.display = 'flex';
        planSummary.style.display = 'none';

        // Clear items except empty state
        const items = planItemsEl.querySelectorAll('.plan-item');
        items.forEach(item => item.remove());
    } else {
        planEmpty.style.display = 'none';
        planSummary.style.display = 'block';

        // Calculate totals
        let totalDist = 0;
        planItems.forEach(item => {
            if (item.distance_from_prev_km) {
                totalDist += item.distance_from_prev_km;
            }
        });

        totalDistance.textContent = `${totalDist.toFixed(1)} km`;
        totalDuration.textContent = `~${Math.round(totalDist / 0.5)} phút`;  // ~30km/h

        // Render items
        renderPlanItems();
    }
}

function renderPlanItems() {
    // Clear existing items
    const existing = planItemsEl.querySelectorAll('.plan-item');
    existing.forEach(el => el.remove());

    // Add items
    planItems.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'plan-item';
        div.draggable = true;
        div.dataset.itemId = item.item_id;

        const distHtml = item.distance_from_prev_km
            ? `<div class="plan-item-distance">+${item.distance_from_prev_km} km</div>`
            : '';

        div.innerHTML = `
            <div class="plan-item-header">
                <span class="plan-order">${index + 1}</span>
                <div class="plan-item-info">
                    <div class="plan-item-name">${item.name}</div>
                    <div class="plan-item-category">${item.category || ''}</div>
                    ${distHtml}
                </div>
                <div class="plan-item-actions">
                    <button class="plan-item-btn" onclick="removeFromPlan('${item.item_id}')" title="Xóa">✕</button>
                </div>
            </div>
        `;

        // Drag events
        div.addEventListener('dragstart', handleDragStart);
        div.addEventListener('dragend', handleDragEnd);
        div.addEventListener('dragover', handleDragOver);
        div.addEventListener('drop', handleDrop);

        planItemsEl.appendChild(div);
    });
}

// Drag and Drop
let draggedItem = null;

function handleDragStart(e) {
    draggedItem = e.target;
    e.target.classList.add('dragging');
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    draggedItem = null;
}

function handleDragOver(e) {
    e.preventDefault();
}

async function handleDrop(e) {
    e.preventDefault();

    if (!draggedItem) return;

    const target = e.target.closest('.plan-item');
    if (!target || target === draggedItem) return;

    // Get new order
    const items = Array.from(planItemsEl.querySelectorAll('.plan-item'));
    const draggedIdx = items.indexOf(draggedItem);
    const targetIdx = items.indexOf(target);

    // Reorder array
    const [removed] = planItems.splice(draggedIdx, 1);
    planItems.splice(targetIdx, 0, removed);

    // Update UI
    renderPlanItems();

    // Send to server
    try {
        const newOrder = planItems.map(p => p.item_id);
        await fetch(`${API_BASE}/planner/${currentPlanId}/reorder?user_id=${CONFIG.userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_order: newOrder })
        });

        // Refresh to get updated distances
        const response = await fetch(`${API_BASE}/planner/${currentPlanId}?user_id=${CONFIG.userId}`);
        if (response.ok) {
            const data = await response.json();
            planItems = data.plan.items;
            updatePlanUI();
        }
    } catch (e) {
        console.error('Reorder error:', e);
    }
}
