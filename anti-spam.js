// АНТИ-СПАМ СИСТЕМА ОТЗЫВОВ
const usedNames = new Set();
const usedReviews = new Set();

function checkDuplicateName(name) {
    const normalizedName = name.trim().toLowerCase();
    if (usedNames.has(normalizedName)) {
        return true; // Имя уже использовано
    }
    usedNames.add(normalizedName);
    return false;
}

function checkDuplicateReview(text) {
    const normalizedText = text.trim().toLowerCase();
    if (usedReviews.has(normalizedText)) {
        return true; // Отзыв уже оставлен
    }
    usedReviews.add(normalizedText);
    return false;
}

function submitReview() {
    const name = document.getElementById('reviewName').value;
    const text = document.getElementById('reviewText').value;
    
    if (!name || !text || selectedRating === 0) {
        alert('Заполните все поля и поставьте оценку!');
        return;
    }
    
    if (checkDuplicateName(name)) {
        alert('Это имя уже оставило отзыв. Пожалуйста, используйте другое имя.');
        return;
    }
    
    if (checkDuplicateReview(text)) {
        alert('Такой отзыв уже существует. Пожалуйста, напишите уникальный отзыв.');
        return;
    }
    
    if (name.length < 2) {
        alert('Имя слишком короткое. Минимум 2 символа.');
        return;
    }
    
    if (text.length < 10) {
        alert('Отзыв слишком короткий. Минимум 10 символов.');
        return;
    }
    
    if (text.length > 500) {
        alert('Отзыв слишком длинный. Максимум 500 символов.');
        return;
    }
    
    // Проверка на мат (лёгкая)
    const badWords = ['бля', 'сука', 'нах', 'хуй', 'пизд', 'еба'];
    const hasBadWord = badWords.some(word => text.toLowerCase().includes(word));
    if (hasBadWord) {
        alert('Пожалуйста, без нецензурной лексики.');
        return;
    }
    
    // Успех
    alert('Спасибо за отзыв! Он появится после модерации.');
    
    // Добавляем отзыв на страницу
    addReviewToPage(name, text, selectedRating);
    
    // Очистка формы
    document.getElementById('reviewName').value = '';
    document.getElementById('reviewText').value = '';
    selectedRating = 0;
    document.querySelectorAll('.rating-star').forEach(s => s.classList.remove('active'));
}

function addReviewToPage(name, text, rating) {
    const reviewsGrid = document.querySelector('.reviews-grid');
    const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);
    
    const reviewCard = document.createElement('div');
    reviewCard.className = 'review-card';
    reviewCard.innerHTML = `
        <div class="review-header">
            <div class="review-avatar">${name.charAt(0).toUpperCase()}</div>
            <div>
                <div class="review-name">${name}</div>
                <div class="review-service">Новый отзыв</div>
            </div>
        </div>
        <div class="stars">${stars}</div>
        <p class="review-text">${text}</p>
        <div class="review-date">Только что</div>
    `;
    
    reviewsGrid.insertBefore(reviewCard, reviewsGrid.firstChild);
}

// Инициализация существующих имён
document.addEventListener('DOMContentLoaded', function() {
    const existingNames = document.querySelectorAll('.review-name');
    existingNames.forEach(el => {
        if (!el.textContent.includes('PHANTOM COMPANY')) {
            usedNames.add(el.textContent.trim().toLowerCase());
        }
    });
});
