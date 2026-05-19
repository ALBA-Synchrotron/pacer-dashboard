const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const messagesRoomName = "messages";
const appContextPath = "{% app_subpath %}";
const socketsContextPath = "{% sockets_subpath %}";
const socketUrl = `${protocol}://${window.location.host}${appContextPath}${socketsContextPath}/ws/${messagesRoomName}/`;


const rws = new ReconnectingWebSocket(socketUrl);

rws.timeoutInterval = 3000;
rws.maxReconnectInterval = 10000;

rws.onopen = function (e) {
    console.log("Connected to Messages WebSocket, welcome");
};

rws.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const msgId = data.message_id;
    htmx.ajax('GET', '{% app_subpath %}/tmpl/messages/' + msgId, {
        target: '#message-results',
        swap: 'afterbegin',
    });
};

rws.onclose = function (e) {
    // reconnecting-websocket lib will automatically try to reconnect
    console.warn("Messages Websocket closed. Reconnecting...");
};

rws.onerror = function (err) {
    console.error("Messages WebSocket Error: ", err);
};