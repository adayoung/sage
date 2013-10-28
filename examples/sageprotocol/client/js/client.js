// WAMP session object
var sess;
var wsuri;
var swindow;
var achaea_connected = false;

window.onload = function() {

   if (window.location.protocol === "file:") {
      wsuri = "ws://localhost:9000";
   } else {
      wsuri = "ws://" + window.location.hostname + ":9000";
   }

   // connect to WAMP server
   ab.connect(wsuri,

      // WAMP session was established
      function (session) {
         sess = session;
         console.log("Connected to Sage");

         sess.prefix("event", "http://sage/event#");
         sess.subscribe("event:instream", instream);
         sess.subscribe("event:connected", connected);

         sess.call('http://sage/is_connected');
      },

      // WAMP session is gone
      function (code, reason) {
         sess = null;
         console.log('Disconnected from Sage');
      }
   );

   swindow = $('#stream-window');

   swindow.height(window.height - 70);
   $(window).resize();

   var input = document.getElementById('main-input');
   input.focus();
   input.select();

   $('#main-input-form').submit(function(e) {
      sess.call("http://sage/input", input.value);
      input.select();
      e.preventDefault();
      return false;
   });
};

function instream(topicUri, event) {
   Object.keys(event.lines).forEach(function (key) {
      if (event.lines[key] === '') {
         swindow.append('<div class="blank line">&nbsp;</div>');
      } else {
         swindow.append('<div class="line">' + ansi_up.ansi_to_html(event.lines[key]) + '</div>');
      }
   });
   swindow.append('<div class="prompt">' + ansi_up.ansi_to_html(event.prompt) + '</div>');
   swindow.scrollTop(swindow[0].scrollHeight);
}

function connected(topicUri, event) {
   if (event === false) {
      $('#main-input').prop('disabled', true);
   } else {
      $('#main-input').prop('disabled', false);
   }
}

$(window).resize(function() {
    swindow.height($(this).height() - 70);
});