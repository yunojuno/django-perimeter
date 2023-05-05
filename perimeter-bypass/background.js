"use strict";

// TODO: read in from options / storage
const SITE1 = { url: "https://*/*", token: "foo" };

// Simple extension to add "X-Perimeter-Token" to requests..
chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    details.requestHeaders.push({
      name: "X-Perimeter-Token",
      value: SITE1.token
    });
    return { requestHeaders: details.requestHeaders };
  },
  // filters
  { urls: [SITE1.url] },
  // extraInfoSpec
  ["blocking", "requestHeaders"]
);
