
const openModalBtn = document.getElementById('openModalBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const addModal = document.getElementById('addModal');
openModalBtn.addEventListener('click', () => {
  addModal.style.display = 'block';
});

closeModalBtn.addEventListener('click', () => {
  addModal.style.display = 'none';
});
window.addEventListener('click', (event) => {
  if (event.target === addModal) {
    addModal.style.display = 'none';
  }
});




const editModal = document.getElementById('editModal');
const closeEditModalBtn = document.getElementById('closeEditModalBtn');

function openEditModal(id, nama) {
  document.getElementById('edit-id').value = id;
  document.getElementById('edit-nama').value = nama;

  editModal.style.display = 'block';
}

closeEditModalBtn.addEventListener('click', () => {
  editModal.style.display = 'none';
});

window.addEventListener('click', (event) => {
  if (event.target === editModal) {
    editModal.style.display = 'none';
  }
});

document.getElementById('editForm').addEventListener('submit', (event) => {
  event.preventDefault(); 
  alert(`Data berhasil disimpan:
    ID: ${document.getElementById('edit-id').value}
    Nama: ${document.getElementById('edit-nama').value}`);
  editModal.style.display = 'none'; 
});




const deleteModal = document.getElementById('deleteModal');
const closeDeleteModalBtn = document.getElementById('closeDeleteModalBtn');
const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

function openDeleteModal(id, nama) {
  document.getElementById('delete-id').value = id;
  document.getElementById('delete-nama').textContent = nama;

  deleteModal.style.display = 'block';
}

closeDeleteModalBtn.addEventListener('click', () => {
  deleteModal.style.display = 'none';
});
cancelDeleteBtn.addEventListener('click', () => {
  deleteModal.style.display = 'none';
});

window.addEventListener('click', (event) => {
  if (event.target === deleteModal) {
    deleteModal.style.display = 'none';
  }
});

document.getElementById('deleteForm').addEventListener('submit', (event) => {
  event.preventDefault(); 
  alert(`Data berhasil dihapus:
    ID: ${document.getElementById('delete-id').value}`);
  deleteModal.style.display = 'none'; 
});
