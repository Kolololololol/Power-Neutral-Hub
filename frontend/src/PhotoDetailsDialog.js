import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Select,
  MenuItem,
  IconButton,
} from '@mui/material';
import { SaveAlt } from '@mui/icons-material';
import Cropper from 'react-easy-crop';
import axios from 'axios';
import config from './config';

const PhotoDetailsDialog = ({ open, onClose, photoData }) => {
  const [editMode, setEditMode] = useState(false);
  const [croppedArea, setCroppedArea] = useState(null);
  const [selectedDefectClass, setSelectedDefectClass] = useState('');
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  const onCropComplete = (croppedArea, croppedAreaPixels) => {
    setCroppedArea(croppedAreaPixels);
  };

  const handleDefectClassChange = (event) => {
    setSelectedDefectClass(event.target.value);
  };

  const handleSave = () => {
    if (!croppedArea || !selectedDefectClass) {
      console.error('Необходимо выбрать область и указать класс дефекта');
      return;
    }

    const dataToSend = {
      photo_id: photoData.photos[currentPhotoIndex].id,
      correct_class: selectedDefectClass,
      x_coord: croppedArea.x,
      y_coord: croppedArea.y,
      width: croppedArea.width,
      height: croppedArea.height,
    };

    axios.post(`${config.backendUrl}/save_misclassified/`, dataToSend)
      .then(response => {
        console.log('Успешно сохранено:', response.data);
        setEditMode(false);
        onClose();
      })
      .catch(error => {
        console.error('Ошибка при сохранении:', error);
      });
  };

  const handleExport = (format) => {
    // URL для получения соответствующего отчета
    const serialNumber = photoData.serial_number;
    let url = `${config.backendUrl}/report/${serialNumber}/${format}`;

    axios.get(url, { responseType: 'blob' })
      .then((response) => {
        // Создание ссылки для загрузки
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${serialNumber}.${format}`); // Имя файла с нужным расширением
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch((error) => {
        console.error('Ошибка при загрузке отчета:', error);
      });
  };

  const handleNextPhoto = () => {
    setCurrentPhotoIndex((prevIndex) => (prevIndex + 1) % photoData.photos.length);
  };

  const handlePreviousPhoto = () => {
    setCurrentPhotoIndex((prevIndex) =>
      prevIndex === 0 ? photoData.photos.length - 1 : prevIndex - 1
    );
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>Детальная информация</DialogTitle>
      <DialogContent>
        <Typography variant="h6">Серийный номер: {photoData.serial_number}</Typography>

        {/* Отображение одной фотографии */}
        <Box sx={{ textAlign: 'center', marginY: 2 }}>
          <Box sx={{ position: 'relative', display: 'inline-block', width: 600, height: 400 }}>
            {editMode ? (
              <Cropper
                image={`${config.backendUrl}/${photoData.photos[currentPhotoIndex].file_path_input}`}
                crop={crop}
                zoom={zoom}
                aspect={4 / 3}
                cropShape="rect"
                onCropChange={(newCrop) => setCrop(newCrop)}
                onZoomChange={(newZoom) => setZoom(newZoom)}
                onCropComplete={onCropComplete}
              />
            ) : (
              <img
                src={`${config.backendUrl}/${photoData.photos[currentPhotoIndex].file_path_output}`}
                alt={`Фото ${currentPhotoIndex + 1}`}
                style={{ width: '100%', height: '100%' }}
              />
            )}
          </Box>

          {/* Кнопки для пролистывания фотографий */}
          <Box sx={{ marginTop: 2, display: 'flex', justifyContent: 'center' }}>
            <Button onClick={handlePreviousPhoto} disabled={photoData.photos.length <= 1}>
              Предыдущее фото
            </Button>
            <Button onClick={handleNextPhoto} disabled={photoData.photos.length <= 1}>
              Следующее фото
            </Button>
          </Box>
        </Box>

        {!editMode && (
        <>
            <Box sx={{ marginTop: 4 }}>
            <Typography variant="h6">Найденные дефекты для устройства:</Typography>
            {photoData.photos.flatMap(photo => photo.results).length > 0 ? (
                photoData.photos.flatMap((photo, photoIndex) =>
                photo.results.map((result, index) => (
                    <Typography key={`${photoIndex}-${index}`} variant="body2" color="text.secondary">
                    - {result.recognized_class} (Фото {photoIndex + 1})
                    </Typography>
                ))
                )
            ) : (
                <Typography variant="body2" color="text.secondary">Нет дефектов</Typography>
            )}
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', marginTop: 2 }}>
            <IconButton onClick={() => handleExport('docx')} color="primary">
                <SaveAlt /> <Typography variant="body2">Word</Typography>
            </IconButton>
            <IconButton onClick={() => handleExport('json')} color="primary">
                <SaveAlt /> <Typography variant="body2">JSON</Typography>
            </IconButton>
            <IconButton onClick={() => handleExport('pdf')} color="primary">
                <SaveAlt /> <Typography variant="body2">PDF</Typography>
            </IconButton>
            </Box>
        </>)}
        {editMode && (
          <>
            <Select
              label="Класс дефекта"
              value={selectedDefectClass}
              onChange={handleDefectClassChange}
              sx={{ marginBottom: 2, marginTop: 2 }}
              fullWidth
            >
              {Object.entries(config.defectClasses).map(([key, value]) => (
                <MenuItem key={key} value={value}>
                  {value}
                </MenuItem>
              ))}
            </Select>
          </>
        )}

      </DialogContent>
      <DialogActions>
        {!editMode ? (
          <Button onClick={() => setEditMode(true)} color="primary">
            Исправить фото
          </Button>
        ) : (
          <Button onClick={handleSave} color="primary">
            Сохранить
          </Button>
        )}
        <Button onClick={onClose} color="secondary">
          Закрыть
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PhotoDetailsDialog;
