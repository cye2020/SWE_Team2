var map = L.map('map').setView([37.2997156, 126.974437], 14);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

function addMarkers(houses) {
    houses.forEach(function (house) {
        var marker = L.marker([house.lat, house.lon]).addTo(map);
        marker.bindPopup(`
            <b>${house.house_type}</b> <b>${house.pay_type}</b><br>
            ${house.direction}  ${house.floor !== null ? `${house.floor}층<br>` : ''}
            ${house.prc !== 0 ? `보증금: ${house.prc}<br>` : ''}
            ${house.rentprc !== 0 ? `월세: ${house.rentprc}<br>` : ''}
            <a class="popup-link" href="/house/${house.house_id}">자세히 보기</a>
        `);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Make a GET request to your Flask API endpoint
    console.log('DOM is ready!');
    fetch('/house/init', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
            // Add any other headers if needed
        }
    })
    .then(response => response.json())
    .then(data => {
        // Data has been successfully fetched
        // Now you can use the data to perform actions on your page
        addMarkers(data);  // Assuming addMarkers is a function that processes the data
    })
    .catch(error => {
        // Handle any errors that occurred during the fetch
        console.error('Error fetching data:', error);
    });
});

function getCheckboxValues(checkboxName) {
    var checkboxes = document.querySelectorAll('input[name="' + checkboxName + '"]:checked');
    var values = [];
    checkboxes.forEach(function (checkbox) {
        values.push(checkbox.value);
    });
    return values;
}

function applyFilters() {
    // Collect filter values
    var houseTypeCheckboxes = document.querySelectorAll('input[name=house_type]:checked');
    var payTypeCheckboxes = document.querySelectorAll('input[name=pay_type]:checked');
    var prcLtInput = document.querySelector('input[name=prc_lt]');
    var rentprcLtInput = document.querySelector('input[name=rentprc_lt]');
    var spc2LtInput = document.querySelector('input[name=space2_lt]');
    // var taglistInput = document.querySelector('input[name=taglist]');
    var directionInput = document.querySelector('input[name=direction]');
    // var sortSelect = document.querySelector('select[name=sort]');
    // var orderSelect = document.querySelector('select[name=order]');

    // Get checkbox values
    var selectedHouseTypes = Array.from(houseTypeCheckboxes).map(checkbox => checkbox.value);
    var selectedPayTypes = Array.from(payTypeCheckboxes).map(checkbox => checkbox.value);
    console.log(selectedHouseTypes);
    // Get input values
    var prcLt = prcLtInput ? (prcLtInput.value.length > 0 ? prcLtInput.value : null) : null;
    var rentprcLt = rentprcLtInput ? (rentprcLtInput.value.length > 0 ? rentprcLtInput.value : null) : null;
    var spc2Lt = spc2LtInput && spc2LtInput.value ? spc2LtInput.value : null;
    // var taglist = taglistInput ? (taglistInput.value.length > 0 ? taglistInput.value : null) : null;
    var direction = directionInput ? (directionInput.value.length > 0 ? directionInput.value : null) : null;

    // Get select values with default values
    // var sort = sortSelect ? (sortSelect.value.length > 0 ? sortSelect.value : 'defaultSortValue') : 'defaultSortValue';
    // var order = orderSelect ? (orderSelect.value.length > 0 ? orderSelect.value : 'defaultOrderValue') : 'defaultOrderValue';

    // Encode filter values
    var filterObject = {
        house_type: selectedHouseTypes,
        pay_type: selectedPayTypes,
        prc_lt: prcLt,
        rentprc_lt: rentprcLt,
        spc2_lt: spc2Lt,
        direction: direction,
    };

    var filterString = Object.keys(filterObject)
        .filter(key => filterObject[key] !== null)
        .map(key => {
            if (Array.isArray(filterObject[key])) {
                console.log(filterObject[key]);
                return filterObject[key].map(value => `${key}[]=${encodeURIComponent(value)}`).join('&');
            } else {
                return `${key}[]=${encodeURIComponent(filterObject[key])}`;
            }
        })
        .join('&');
    
    function clearMarkers() {
        map.eachLayer(function (layer) {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });
    }

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/house/filter?' + filterString, true);
    console.log('Request URL:', '/house/filter?' + filterString);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Clear existing markers
            clearMarkers();

            // Update map with filtered houses
            var serverData = JSON.parse(xhr.responseText);
            var houseCount = serverData.length; // assuming 'house' is an array in the response
            console.log('Number of Houses:', houseCount);

            // Call the addMarkers function with the received data
            addMarkers(serverData);
        } else if (xhr.readyState === 4) {
            console.error('Error:', xhr.status);
        }
    };
    xhr.send();
}

function resetFilters() {
    var filterInputs = document.querySelectorAll('input[type="checkbox"], input[type="number"], input[type="text"]');
    console.log(filterInputs);
    filterInputs.forEach(function (input) {
        if (input.type === 'checkbox') {
            input.checked = false;
        }
        else{
            input.value = '';
        }
    });
    console.log('After Reset - Checkbox States:', Array.from(document.querySelectorAll('input[type="checkbox"]')).map(checkbox => checkbox.checked));   
    console.log('Reset start');
    fetch('/house/filter?reset=true', {  // Add the reset parameter
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
            // Add any other headers if needed
        }
    })
    .then(response => response.json())
    .then(data => {
        // Data has been successfully fetched
        // Now you can use the data to perform actions on your page
        addMarkers(data);  // Assuming addMarkers is a function that processes the data
    })
    .catch(error => {
        // Handle any errors that occurred during the fetch
        console.error('Error fetching data:', error);
    });
}