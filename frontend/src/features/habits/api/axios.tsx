import axios from 'axios';

const axiosCreate = axios.create({
    baseURL: 'http://localhost:5173'
});

export default axiosCreate;