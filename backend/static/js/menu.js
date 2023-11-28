// Get references to the icon elements
const homeIcon = document.getElementById('homeIcon');
const estateIcon = document.getElementById('estateIcon');
const bulletinIcon = document.getElementById('bulletinIcon');
const logoutIcon = document.getElementById('logoutIcon');

// Add click event listeners
homeIcon.addEventListener('click', () => {
    // Navigate to the home page
    window.location.href = '/home';
});

estateIcon.addEventListener('click', () => {
    // Navigate to the estate page
    window.location.href = '/house';
});

bulletinIcon.addEventListener('click', () => {
    // Navigate to the bulletin page
    window.location.href = '/board';
});


logoutIcon.addEventListener('click', () => {
    // Redirect to the logout page
    window.location.href = '/logout';
});

