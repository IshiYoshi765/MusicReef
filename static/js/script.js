// 削除の確認モーダル
const deleteModal = document.querySelector(".delete-modal");
const deleteMusicId = document.querySelector(".delete-music-id");

const modalButtons = document.querySelectorAll(".js-delete-modal-button");
modalButtons.forEach((elm, i) => {
  elm.addEventListener("click", (e) => {
    let music = e.target.dataset.music;
    console.log(music);
    deleteMusicId.setAttribute("value", music);
    deleteModal.classList.add("is-open");
  });
});
//モーダルの閉じるボタン
const modalClose = document.querySelector(".js-delete-close-button");
modalClose.addEventListener("click", () => {
  deleteModal.classList.remove("is-open");
});

//詳細モーダルーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
function openModal(
  name,
  genre,
  detail,
  length,
  composer,
  source,
  URL,
  date_register,
  update_time
) {
  // date_registerとupdate_timeをtoLocaleString()メソッドで適切な形式に変換
  const formattedDateRegister = new Date(date_register).toLocaleString();
  const formattedUpdateDate = new Date(update_time).toLocaleString();

  // URLをリンクとして表示する
  const urlLink = URL
    ? `<p>URL: <a href="${URL}" target="_blank">${URL}</a></p>`
    : "";

  document.getElementById("modal-body1").innerHTML = `
      <p>曲名: ${name}</p>
      <p>ジャンル: ${genre}</p>
      <p>詳細: ${detail}</p>
      <p>長さ: ${length}</p>
      <p>作曲家: ${composer}</p>
      <p>参照元: ${source}</p>
      ${urlLink}
      <p>登録日時: ${formattedDateRegister}</p>
      <p>更新日時: ${formattedUpdateDate}</p>

  `;

  document.querySelector(".layer.detail-modal").classList.add("is-open");
}

function closeModal() {
  document.querySelector(".layer.detail-modal").classList.remove("is-open");
}
//ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

// 口コミのモーダルーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
document.addEventListener("DOMContentLoaded", function () {
  // 何らかの初期化処理
});

// 口コミ一覧を取得して表示する関数
function fetchAndOpenReviewModal(musicId) {
  // ここでサーバーサイドのAPIを呼び出して音源情報と口コミデータを取得
  fetch(`/api/musicinfo?music_id=${musicId}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      // 取得したデータを表示
      displayMusicInfoAndReviews(data);
      // モーダルを表示
      openReviewModal();
    })
    .catch((error) => console.error("Error fetching data:", error));
}

// 取得したデータを表示する関数
function displayMusicInfoAndReviews(data) {
  let modalBody = document.getElementById("reviewList");
  modalBody.innerHTML = "";

  // 口コミ一覧を表示
  data.reviews.forEach(function (review) {
    let reviewItem = document.createElement("div");
    reviewItem.innerHTML = `<div style="display: flex;">
    <p style="margin-left: 10px;">★: ${review[3]}</p>
    <p style="margin-left: 40px;">口コミ: ${review[4]}</p>
  </div>`;
    modalBody.appendChild(reviewItem);
  });
  document.querySelector(".layer.review-modal").classList.add("is-open");
}

function closeReviewModal() {
  document.querySelector(".layer.review-modal").classList.remove("is-open");
}
//ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
