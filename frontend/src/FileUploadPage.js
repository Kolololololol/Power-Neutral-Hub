import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, List, ListItem, ListItemText } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import config from './config';

const FileUploadPage = () => {
  const [files, setFiles] = useState([]);
  const [serialNumber, setSerialNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const { getRootProps, getInputProps } = useDropzone({
    accept: 'image/*,application/zip,application/x-rar-compressed',
    onDrop: (acceptedFiles) => {
      setFiles([...files, ...acceptedFiles]);
    },
  });

  const handleSerialNumberChange = (event) => {
    setSerialNumber(event.target.value);
  };

  const handleSubmit = () => {
    if (!serialNumber || files.length === 0) {
      setError('Пожалуйста, введите серийный номер и добавьте хотя бы один файл.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('serial_number', serialNumber);
    files.forEach((file) => {
      formData.append('files', file);
    });

    axios.post(`${config.backendUrl}/upload/`, formData)
      .then(response => {
        setSuccess('Файлы успешно загружены и обработаны.');
        setFiles([]);
        setSerialNumber('');
      })
      .catch(error => {
        setError('Ошибка загрузки файлов: ' + (error.response?.data?.error || error.message));
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" gutterBottom>Загрузка файлов</Typography>

      {/* Поле для серийного номера */}
      <TextField
        label="Серийный номер"
        variant="outlined"
        fullWidth
        value={serialNumber}
        onChange={handleSerialNumberChange}
        sx={{ marginBottom: 2 }}
      />

      {/* Поле для Drag and Drop */}
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed grey',
          padding: 4,
          cursor: 'pointer',
          textAlign: 'center',
          marginBottom: 2,
        }}
      >
        <input {...getInputProps()} />
        <Typography variant="body1">Перетащите файлы сюда или кликните для выбора (изображения или архивы)</Typography>
      </Box>

      {/* Отображение выбранных файлов в виде списка */}
      {files.length > 0 && (
        <List sx={{ marginBottom: 2, width: '100%' }}>
          {files.map((file, index) => (
            <ListItem key={index} sx={{ borderBottom: '1px solid #ccc' }}>
              <ListItemText primary={file.name} />
            </ListItem>
          ))}
        </List>
      )}

      {/* Кнопка для отправки данных */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? 'Загрузка...' : 'Отправить'}
      </Button>

      {/* Уведомления об ошибке или успехе */}
      {error && (
        <Alert severity="error" sx={{ marginTop: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ marginTop: 2 }}>
          {success}
        </Alert>
      )}
    </Box>
  );
};

export default FileUploadPage;
