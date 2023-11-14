//削除の確認モーダル
const modal = document.querySelector('.delete-modal');
const modalButtons = document.querySelectorAll('.js-delete-modal-button');
modalButtons.forEach((elm,i) =>{
  elm.addEventListener('click', () => {
    modal.classList.add('is-open')
 })
})

//モーダルの閉じるボタン
const modalClose = document.querySelector('.js-delete-close-button');
modalClose.addEventListener('click', () => {
  modal.classList.remove('is-open');
});

//詳細のモーダル
const modal2 = document.querySelector('.detail-modal');
const modalButton2 = document.querySelectorAll('.js-detail-modal-button');  /*.はclassの取得*/
modalButton2.forEach((elm,i) =>{
  elm.addEventListener('click', () => {
    modal.classList.add('is-open')
  })
});
//モーダルの閉じるボタン
const modalClose2 = document.querySelector('.js-detail-close-button');
modalClose2.addEventListener('click', () => {
  modal2.classList.remove('is-open');
});