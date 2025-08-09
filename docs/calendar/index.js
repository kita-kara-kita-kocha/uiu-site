document.addEventListener('DOMContentLoaded', () => {
    const calendar = document.getElementById('calendar');
    const yearMonth = document.getElementById('year-month');

    const today = new Date();
    let year = today.getFullYear();
    let month = today.getMonth();
    const date = today.getDate();

    // Set year and month
    yearMonth.textContent = `${year}年 ${month + 1}月`;

    const loader = document.createElement('div');
    loader.id = 'loader';
    document.body.appendChild(loader);

    // Show loader before API request
    loader.style.display = 'block';

    const apiUrl = 'https://script.google.com/macros/s/AKfycbyzR2KODZn0JbfJ0084RTDgHLsbV-hE9ZKd1IyBW9s4ob2bkKGSIqFYDmeYmVN-FEQp/exec';

    // Fetch data from local JSON files and API
    Promise.all([
        fetch('../youtube.json').then(res => res.json()),
        fetch('../niconico_l.json').then(res => res.json()),
        fetch('../fciu.json').then(res => res.json()),
        fetch(apiUrl).then(res => res.json())
    ])
    .then(([youtubeData, niconicoData, fciuData, apiData]) => {
        const allEvents = [
            ...youtubeData.items.map(item => ({
                type: 'youtube',
                date: item.upload_date,
                title: item.title,
                description: item.description,
            })),
            ...niconicoData.items.map(item => ({
                type: 'niconico',
                date: item.upload_date,
                title: item.title,
                description: "-"
            })),
            ...fciuData.items.map(item => ({
                type: 'fciu',
                date: item.upload_date,
                title: item.title,
                description: item.metadata[-1]
            })),
            ...apiData.data
        ];

        // Remove direct rendering of events inside the calendar
        // Only add dots to indicate events on specific dates
        allEvents.forEach(event => {
            const date = new Date(event.date);
            if (isNaN(date.getTime())) {
                console.warn('Invalid date for event:', event);
                return; // Skip invalid dates
            }
            const dateCell = document.querySelector(`[data-date="${date.toISOString().split('T')[0]}"]`);
            if (dateCell) {
                const dot = document.createElement('span');
                dot.classList.add('event-dot');
                dateCell.appendChild(dot);
            }
        });

        // デバッグ用: 取得したデータをログに出力
        console.log('YouTube Data:', youtubeData);
        console.log('Niconico Data:', niconicoData);
        console.log('FCIU Data:', fciuData);
        console.log('API Data:', apiData);

        // モーダルウィンドウ関連の処理
        const modal = document.getElementById('modal');
        const modalEvents = document.getElementById('modal-events');
        const closeButton = document.querySelector('.close-button');

        closeButton.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Add click event to calendar days
        document.querySelectorAll('.day').forEach(day => {
            day.addEventListener('click', () => {
                const date = day.getAttribute('data-date');
                const eventsForDate = allEvents.filter(event => {
                    const eventDate = new Date(event.date);
                    if (isNaN(eventDate.getTime())) {
                        console.warn('Invalid date for event in modal:', event);
                        return false; // Skip invalid dates
                    }
                    return eventDate.toISOString().split('T')[0] === date;
                });

                modalEvents.innerHTML = '';
                eventsForDate.forEach(event => {
                    const eventElement = document.createElement('div');
                    eventElement.classList.add('event');
                    eventElement.innerHTML = `
                        <h3>${event.title}</h3>
                        <p>${new Date(event.date).toLocaleDateString()}</p>
                        <p>${event.description}</p>
                    `;
                    modalEvents.appendChild(eventElement);
                });

                modal.style.display = 'block';
            });
        });
    })
    .catch(error => console.error('Error fetching data:', error))
    .finally(() => {
        // Hide loader after API request
        loader.style.display = 'none';
    });

    let currentYear = year;
    let currentMonth = month;

    function renderCalendar(year, month) {
        calendar.innerHTML = '';
        yearMonth.textContent = `${year}年 ${month + 1}月`;

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'day';
            calendar.appendChild(emptyDay);
        }

        for (let i = 1; i <= daysInMonth; i++) {
            const day = document.createElement('div');
            day.className = 'day';
            day.textContent = i;
            const fullDate = new Date(year, month, i);
            day.setAttribute('data-date', fullDate.toISOString().split('T')[0]);
            if (i === date && year === today.getFullYear() && month === today.getMonth()) {
                day.classList.add('current-day');
            }
            calendar.appendChild(day);
        }
    }

    const prevButton = document.createElement('dev');
    prevButton.id = 'prev-month';
    prevButton.textContent = '前月';
    yearMonth.parentElement.insertBefore(prevButton, yearMonth);

    const nextButton = document.createElement('dev');
    nextButton.id = 'next-month';
    nextButton.textContent = '次月';
    yearMonth.parentElement.insertBefore(nextButton, prevButton.nextSibling);

    prevButton.addEventListener('click', () => {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar(currentYear, currentMonth);
    });

    nextButton.addEventListener('click', () => {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar(currentYear, currentMonth);
    });

    renderCalendar(currentYear, currentMonth);
});
