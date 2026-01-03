document.addEventListener("DOMContentLoaded", () => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    const userId = tg.initDataUnsafe?.user?.id;

    function applyTheme() {
        const theme = tg.themeParams || {};
        const root = document.documentElement;
        const isDark = tg.colorScheme === 'dark';
        root.setAttribute('data-theme', isDark ? 'dark' : 'light');
        root.style.setProperty("--bg", theme.bg_color || "#ffffff");
        root.style.setProperty("--text", theme.text_color || "#000000");
        root.style.setProperty("--sec-bg", theme.secondary_bg_color || "#f4f4f4");
        root.style.setProperty("--accent", theme.button_color || "#3390ec");
    }

    applyTheme();
    tg.onEvent('themeChanged', applyTheme);

    function scrollToToday() {
        const container = document.querySelector('.scroll-container');
        const todayEl = document.querySelector('.fc-day-today');

        if (todayEl && container) {
            const scrollPos = todayEl.offsetLeft - 50;
            container.scrollTo({
                left: scrollPos > 0 ? scrollPos : 0,
                behavior: 'smooth'
            });
        }
    }

    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        height: 'auto',
        slotMinTime: "07:00:00",
        slotMaxTime: "20:00:00",
        slotDuration: '00:30:00',
        slotLabelInterval: '01:00:00',
        slotLabelFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
        allDaySlot: false,
        firstDay: 1,
        hiddenDays: [0],
        locale: 'uk',

        // Добавляем кастомную кнопку для управления скроллом
        customButtons: {
            todayBtn: {
                text: 'Сьогодні',
                click: function() {
                    calendar.today();
                    setTimeout(scrollToToday, 100);
                }
            }
        },
        headerToolbar: {
//            left: 'todayBtn timeGridWeek,timeGridDay',
            left: 'todayBtn',
            center: 'title',
            right: 'prev,next'
        },

        titleFormat: { day: '2-digit', month: '2-digit' },
        titleRangeSeparator: ' - ',
        dayHeaderFormat: { weekday: 'short', day: '2-digit' },
        nowIndicator: true,
        scrollTime: "08:00:00",
        slotEventOverlap: false,
        eventMinHeight: 45,

        eventClick: function(info) {
            const props = info.event.extendedProps;
            if (info.el) { info.el.blur(); }

            tg.showPopup({
                title: props.subjectName,
                message: `⏰ Час: ${props.rawTime}\n📚 Тип: ${props.fullType}`,
                buttons: [{type: 'close', text: 'Зрозуміло'}]
            });
        },

        eventContent: function(arg) {
            const props = arg.event.extendedProps;
            return {
                html: `
                    <div class="fc-event-time">${props.customTime}</div>
                    <div class="fc-event-title">${props.subjectName}</div>
                    <div class="fc-event-type">${props.shortType}</div>
                `
            };
        }
    });

    calendar.render();
    setTimeout(scrollToToday, 300);

    fetch(`/api/week?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            const events = [];
            const typeClassMap = {
                "Пз": "type-pz", "Лк": "type-lk", "Лб": "type-lb",
                "Конс": "type-cons", "ІспКомб": "type-exam", "Зал": "type-zal"
            };

            for (const date in data) {
                const dayData = data[date];
                if (!dayData || dayData.length <= 2) continue;

                const parts = date.split(".");
                const isoDate = `${parts[2]}-${parts[1].padStart(2,"0")}-${parts[0].padStart(2,"0")}`;

                dayData.slice(2).forEach(lec => {
                    lec.info.forEach(item => {
                        events.push({
                            title: item[0],
                            start: `${isoDate}T${lec.start}:00`,
                            end: `${isoDate}T${lec.end}:00`,
                            classNames: [typeClassMap[item[1]] || 'type-default'],
                            extendedProps: {
                                subjectName: item[0],
                                shortType: item[1],
                                fullType: item[2] || item[1],
                                customTime: `${lec.start} - <br>${lec.end}`,
                                rawTime: `${lec.start} - ${lec.end}`
                            }
                        });
                    });
                });
            }
            calendar.addEventSource(events);
            setTimeout(scrollToToday, 500);
        });
});