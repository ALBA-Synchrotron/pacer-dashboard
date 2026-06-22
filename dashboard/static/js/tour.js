const driver = window.driver.js.driver;

const driverObj = driver({
    showProgress: true,
    onDestroyed: function () {
        localStorage.setItem('first-tour-passed', 'true');
    },
    steps: [
        {
            element: '#tour-dashboard-overview',
            popover:
                {
                    title: 'Welcome to the PACER\'s dashboard',
                    description: 'Take a tour of the dashboard to learn more about the features available.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-first-msg',
            popover:
                {
                    title: 'This is a message',
                    description: 'All messages processed by the PACER are displayed here along their payload, ' +
                        'hash and other details.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-action-ack',
            popover:
                {
                    title: 'Message acknowledged',
                    description: 'You can mark a message as acknowledged by clicking the button below.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-action-resend',
            popover:
                {
                    title: 'Message reingestion',
                    description: 'You can send a message over for reingestion through here while modifying its payload ' +
                        'or even rerouting it to a different queue.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-action-related',
            popover:
                {
                    title: 'Related messages',
                    description: 'Some messages can be forwarded internally between different queues. Here you can view' +
                        ' all the times a message has been processed in the context of an ingestion pipeline.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-msg-obj-identifiers',
            popover:
                {
                    title: 'Object identifiers',
                    description: 'In addition to its payload and hash, each message also contains a set of identifiers ' +
                        'to enable easy human-readability and filtering.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-navbar',
            popover:
                {
                    title: 'Filters',
                    description: 'You can filter through message or payload types, dates, and other attributes through' +
                        ' the search box.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-stream-live',
            popover:
                {
                    title: 'Live updates',
                    description: 'If enabled, new messages will be displayed and updated in real-time.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-theme-toggle',
            popover:
                {
                    title: 'Light protection',
                    description: 'Dark mode is available if you care about your eyes.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-stats',
            popover:
                {
                    title: 'Statistics',
                    description: 'Overall statistics of the PACER operation can be found here.',
                    side: "left", align: 'start'
                }
        },
        {
            element: '#tour-again',
            popover:
                {
                    title: 'Take the tour again',
                    description: 'If you want to take the tour again, click here.',
                    side: "left", align: 'start'
                }
        },

    ]
});