import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Card, CardContent, CardMedia, Typography, Grid, Button } from '@mui/material';
import PhotoDetailsDialog from './PhotoDetailsDialog';
import config from './config';

const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPhotoData, setSelectedPhotoData] = useState(null);

  useEffect(() => {
    axios.get(`${config.backendUrl}/history/`)
      .then(response => {
        setHistory(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, []);

  const handleDetailsClick = (serialNumber) => {
    axios.get(`${config.backendUrl}/history/${serialNumber}`)
      .then(response => {
        setSelectedPhotoData(response.data);
      })
      .catch(error => {
        console.error('Ошибка при получении данных:', error);
      });
  };

  const handleCloseDialog = () => {
    setSelectedPhotoData(null);
  };

  if (loading) {
    return <Typography>Загрузка...</Typography>;
  }

  if (error) {
    return <Typography color="error">Ошибка загрузки данных: {error.message}</Typography>;
  }

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" gutterBottom>История</Typography>
      <Grid container spacing={3}>
        {history.map((item, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card>
              <CardMedia
                component="img"
                height="140"
                image={`${config.backendUrl}/${item.photo}`}
                alt={`Фото для серийного номера ${item.serial_number}`}
              />
              <CardContent>
                <Typography variant="h6">Серийный номер: {item.serial_number}</Typography>
                <Typography variant="body2" color="text.secondary">Дата обработки: {item.date}</Typography>
              </CardContent>
              <Button size="small" onClick={() => handleDetailsClick(item.serial_number)}>Подробнее</Button>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Всплывающее окно с подробной информацией */}
      {selectedPhotoData && (
        <PhotoDetailsDialog
          open={true}
          onClose={handleCloseDialog}
          photoData={selectedPhotoData}
        />
      )}
    </Box>
  );
};

export default HistoryPage;
