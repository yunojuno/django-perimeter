// TODO: improve UI, support more than one token

// Saves options to chrome.storage
function save_options() {
  var url1 = document.getElementById("site1").value;
  var token1 = document.getElementById("token1").value;
  chrome.storage.sync.set(
    {
      site1: { url: url1, token: token1 }
    },
    function() {
      // Update status to let user know options were saved.
      var status = document.getElementById("status");
      status.textContent = "Options saved.";
      setTimeout(function() {
        status.textContent = "";
      }, 750);
    }
  );
}

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options() {
  // Use default value color = 'red' and likesColor = true.
  chrome.storage.sync.get(["site1"], function(items) {
    document.getElementById("site1").value = items.site1.url;
    document.getElementById("token1").value = items.site1.token;
  });
}
document.addEventListener("DOMContentLoaded", restore_options);
document.getElementById("save").addEventListener("click", save_options);
