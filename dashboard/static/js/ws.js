

let rws;

function initWebSocket() {
    if (!rws){
        rws = new ReconnectingWebSocket(socketUrl);
        rws.timeoutInterval = 3000;
        rws.maxReconnectInterval = 10000;

        rws.onopen = function (e) {
            console.log("Connected to Messages WebSocket, welcome");
        };

        rws.onmessage = function (e) {
            const data = JSON.parse(e.data);
            const msgId = data.message_id;
            htmx.ajax('GET', messageFetchUrl + msgId, {
                target: '#message-results',
                swap: 'afterbegin',
                source: '#general-text-search',
            });
        };

        rws.onclose = function (e) {
            // reconnecting-websocket lib will automatically try to reconnect
            console.warn("Messages Websocket closed. Reconnecting...");
        };

        rws.onerror = function (err) {
            console.error("Messages WebSocket Error: ", err);
        };
    }
}

function toggleWS() {
    if ( document.getElementById("live-enabled").checked) {
        initWebSocket();
    }else{
        rws.close();
        rws = null;
    }
}

if(document.getElementById("live-enabled").checked){
    initWebSocket()
}
