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

    const loader = document.createElement('div');
    loader.id = 'loader';
    document.body.appendChild(loader);

    // Show loader before API request
    loader.style.display = 'block';

    const apiUrl = 'https://script.google.com/macros/s/AKfycbyzR2KODZn0JbfJ0084RTDgHLsbV-hE9ZKd1IyBW9s4ob2bkKGSIqFYDmeYmVN-FEQp/exec';

    const localFiles = ['../youtube.json', '../niconico_l.json', '../fciu.json'];
    const localEvents = [];

    // Fetch data from local JSON files
    Promise.all(localFiles.map(file => fetch(file).then(response => response.json())))
        .then(localData => {
            localData.forEach(data => {
                if (Array.isArray(data)) {
                    localEvents.push(...data);
                }
            });

            // Add local events to the calendar
            localEvents.forEach(event => {
                const date = new Date(event.date);
                const dateCell = document.querySelector(`[data-date="${date.toISOString().split('T')[0]}"]`);
                if (dateCell) {
                    const dot = document.createElement('span');
                    dot.classList.add('event-dot');
                    dateCell.appendChild(dot);
                }
            });
        })
        .catch(error => console.error('Error fetching local data:', error))
        .finally(() => {
            // Fetch data from the API
            fetch(apiUrl)
                .then(response => response.json())
                .then(data => {
                    const events = data.data;

                    // Add API events to the calendar
                    events.forEach(event => {
                        const date = new Date(event.date);
                        const dateCell = document.querySelector(`[data-date="${date.toISOString().split('T')[0]}"]`);
                        if (dateCell) {
                            const dot = document.createElement('span');
                            dot.classList.add('event-dot');
                            dateCell.appendChild(dot);
                        }
                    });

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
                            const eventsForDate = [...localEvents, ...events].filter(event => new Date(event.date).toISOString().split('T')[0] === date);

                            modalEvents.innerHTML = '';
                            eventsForDate.forEach(event => {
                                const eventElement = document.createElement('div');
                                eventElement.classList.add('event');
                                eventElement.innerHTML = `
                                    <h3>${event.title}</h3>
                                    <p>${new Date(event.date).toLocaleDateString()} ${new Date(event.time).toLocaleTimeString()}</p>
                                    <p>${event.description || event.subscription}</p>
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
        });
});
