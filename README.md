# alfred-jsonviewer

An alfred workflow help you to get a good json view.

Get JSON from clipboard then show it in Chrome.

## Depends
* Google Chrome
* (Optional)Google Chrome JSON Plugin(choose either one)
  * [JSONVue](https://chrome.google.com/webstore/detail/jsonvue/chklaanhfefbnpoihckbnefhakgolnmc)
  * [JSON Viewer](https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh)
  * [JSON Formatter](https://chrome.google.com/webstore/detail/json-formatter/bcjindcccaagfpapjjmafapmmgkkhgoa)

## Usage

### Basic

![Kapture 2022-12-24 at 23 41 41](https://user-images.githubusercontent.com/15275771/209442907-0a8fdca4-af7d-430a-8b1c-b737fb46d3d7.gif)

1. Copy a JSON object into your clipboard
2. Input `json` then click enter key

### Find Sub JSON Object

![Kapture 2022-12-24 at 23 37 30](https://user-images.githubusercontent.com/15275771/209442823-bdde04a6-c8df-4fca-ba68-c0c1d4117b67.gif)

1. Copy a JSON object into your clipboard
2. Input `json`
3. Find a key in drop-down list and use tab to fill the key word
4. Input `>` to determine a key path and go into the sub JSON Object(string formatted JSON object also can unfold)
5. Repeat 3,4 when find the aimed hierarchy
6. Click enter key
