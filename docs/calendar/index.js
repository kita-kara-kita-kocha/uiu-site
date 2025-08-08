document.addEventListener('DOMContentLoaded', () => {
    const calendar = document.getElementById('calendar');
    const yearMonth = document.getElementById('year-month');

    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();
    const date = today.getDate();

    // Set year and month
    yearMonth.textContent = `${year}年 ${month + 1}月`;

    // Generate days for a simple calendar
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Fill empty days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'day';
        calendar.appendChild(emptyDay);
    }

    // Fill days of the month
    for (let i = 1; i <= daysInMonth; i++) {
        const day = document.createElement('div');
        day.className = 'day';
        day.textContent = i;
        // Add data-date attribute to each day
        const fullDate = new Date(year, month, i);
        day.setAttribute('data-date', fullDate.toISOString().split('T')[0]);
        if (i === date) {
            day.classList.add('current-day');
        }
        calendar.appendChild(day);
    }
});
