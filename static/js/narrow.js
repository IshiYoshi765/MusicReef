document.addEventListener("DOMContentLoaded", function () {
  // 絞り込みおよび並べ替え関数
  function filterAndSortMusic() {
    // 絞り込み条件を取得
    var musicLength = document.querySelector(".music-length").value;
    var selectedSite = document.querySelector(".site").value;

    // 音楽リストの各要素を取得
    var musicEntries = document.querySelectorAll(".music-entry");

    // 各音楽エントリーに対して絞り込み条件を適用
    let count = 0;
    musicEntries.forEach(function (entry) {
      // 絞り込み条件を取得
      let musicLengthData = document.querySelectorAll("#music-length-data");
      let musicLengthNumber = musicLengthData[count].dataset.length;

      let musicSiteData = document.querySelectorAll("#music-site-data");
      let musicDataNumber = musicSiteData[count].dataset.site;

      // 絞り込み条件を満たすか確認
      var siteMatch = selectedSite === "" || selectedSite === musicDataNumber;
      var lengthMatch = musicLength === "" || musicLength === musicLengthNumber;

      // 絞り込み条件を満たす場合は表示、そうでなければ非表示
      if (siteMatch && lengthMatch) {
        entry.style.display = "flex"; // 表示に変更
      } else {
        entry.style.display = "none";
      }
      count++;
    });

    // プルダウンのフォーカスを外すことでCSSの崩れを防ぐ
    document.activeElement.blur();
  }

  // プルダウンリストが変更されたときに filterAndSortMusic 関数を呼び出す
  document
    .querySelector(".music-length")
    .addEventListener("change", filterAndSortMusic);
  document
    .querySelector(".site")
    .addEventListener("change", filterAndSortMusic);
});
