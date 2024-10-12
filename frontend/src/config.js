// const backendUrl = "https://339d-46-62-80-248.ngrok-free.app";
const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:5001";

const defectClasses = {0: 'царапина',
                        1: 'битый пиксель',
                        2: 'дефект клавиатуры',
                        3: 'некорректно смонтирован замок',
                        4: 'отсутствует шуруп',
                        5: 'скол',
                        6: 'поврежден логотип',
                        7: 'дефект матрицы'}

export default {backendUrl, defectClasses};