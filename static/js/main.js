// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Handle race deletion
    var deleteRaceModal = document.getElementById('deleteRaceModal')
    if (deleteRaceModal) {
        deleteRaceModal.addEventListener('show.bs.modal', function (event) {
            // Button that triggered the modal
            var button = event.relatedTarget
            
            // Extract info from data-* attributes
            var raceId = button.getAttribute('data-race-id')
            var raceName = button.getAttribute('data-race-name')
            
            // Update the modal's content
            var raceNameElement = deleteRaceModal.querySelector('#raceNameToDelete')
            var deleteForm = deleteRaceModal.querySelector('#deleteRaceForm')
            
            raceNameElement.textContent = raceName
            deleteForm.action = `/races/${raceId}/delete/`
        })
    }
});