//管理者 削除の確認モーダル
const adminDeleteModal = document.querySelector(".admin-delete-modal")
const deleteAdminId = document.querySelector(".delete-admin-id")

const adminDeleteModalButton = document.querySelectorAll('.js-admin-delete-modal-button')
adminDeleteModalButton.forEach((elm, i) => {
  elm.addEventListener("click", (e) => {
    let adminId = e.target.dataset.admin;
    console.log(adminId);
    deleteAdminId.setAttribute("value", adminId);
    adminDeleteModal.classList.add("is-open");
  });
});

//モーダルの閉じるボタン
const adminDeleteModalClose = document.querySelector(".js-admin-delete-close-button");
adminDeleteModalClose.addEventListener("click", () => {
  adminDeleteModal.classList.remove("is-open");
});

//凍結モーダル
const adminFreezeModal = document.querySelector('.admin-freeze-modal')
const adminFreezeButton = document.querySelectorAll(".admin-freeze-button")

const freezeAdminId = document.querySelector(".cold-admin-id")

adminFreezeButton.forEach((elm,i) =>{
  elm.addEventListener("click",(e) =>{
    let freezAdmin = e.target.dataset.admin;
    console.log(freezAdmin);
    freezeAdminId.setAttribute("value", freezAdmin);
    adminFreezeModal.classList.add("is-open");
  });
});

//モーダルの閉じるボタン
const freezeCloseButton = document.querySelector(".js-freeze-close-button");
freezeCloseButton.addEventListener("click", () => {
  adminFreezeModal.classList.remove("is-open");
});