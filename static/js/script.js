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

  document.getElementById("modal-body1").innerHTML = `
      <p>曲名: ${name}</p>
      <p>ジャンル: ${genre}</p>
      <p>詳細: ${detail}</p>
      <p>長さ: ${length}</p>
      <p>作曲家: ${composer}</p>
      <p>参照元: ${source}</p>
      <p>URL: ${URL}</p>
      <p>登録日時: ${formattedDateRegister}</p>
      <p>更新日時: ${formattedUpdateDate}</p>
      <button class="js-detail-close-button" onclick="closeModal()">閉じる</button>
  `;

  document.querySelector(".layer.detail-modal").classList.add("is-open");
}

function closeModal() {
  document.querySelector(".layer.detail-modal").classList.remove("is-open");
}
//ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

// 口コミのモーダル
const reviewModal = document.querySelector(".review-modal");

const reviewModalButtons = document.querySelectorAll(".js-review-modal-button");
reviewModalButtons.forEach((elm, i) => {
  elm.addEventListener("click", (e) => {
    reviewModal.classList.add("is-open");
  });
});
//モーダルの閉じるボタン
const modalClose2 = document.querySelector(".js-review-close-button");
modalClose2.addEventListener("click", () => {
  reviewModal.classList.remove("is-open");
});