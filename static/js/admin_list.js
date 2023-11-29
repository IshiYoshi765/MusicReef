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

