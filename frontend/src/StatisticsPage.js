import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Card, CardContent, Typography, Grid, CircularProgress } from '@mui/material';
import { Assignment, ErrorOutline, PhotoLibrary } from '@mui/icons-material';
import config from './config';

const StatisticsPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${config.backendUrl}/statistics/`)
      .then(response => {
        setStats(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', padding: 4 }}>
        <Typography color="error" variant="h5">Ошибка загрузки данных: {error.message}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', textAlign: 'center' }}>Статистика</Typography>
      <Grid container spacing={3}>
        {/* Общая статистика */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ backgroundColor: '#e0f7fa', boxShadow: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assignment sx={{ fontSize: 40, color: '#00796b' }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold', marginTop: 1 }}>Распознано объектов</Typography>
              <Typography variant="h3" color="primary" sx={{ fontWeight: 'bold' }}>{stats.recognized_objects}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ backgroundColor: '#ffebee', boxShadow: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <ErrorOutline sx={{ fontSize: 40, color: '#d32f2f' }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold', marginTop: 1 }}>Найдено дефектов</Typography>
              <Typography variant="h3" color="error" sx={{ fontWeight: 'bold' }}>{stats.detected_defects}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ backgroundColor: '#e3f2fd', boxShadow: 3 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <PhotoLibrary sx={{ fontSize: 40, color: '#1565c0' }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold', marginTop: 1 }}>Число загруженных фотографий</Typography>
              <Typography variant="h3" color="secondary" sx={{ fontWeight: 'bold' }}>{stats.photos_uploaded}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Отображение статистики по классам */}
        {Object.entries(config.defectClasses).map(([classId, className]) => (
          <Grid item xs={12} sm={6} md={4} key={classId}>
            <Card sx={{ backgroundColor: '#fafafa', boxShadow: 2 }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Класс: {className}</Typography>
                <Typography variant="h4" color="textPrimary" sx={{ fontWeight: 'bold' }}>{stats.class_stats[className] || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}

        {/* Изменения за день, неделю, месяц */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', textAlign: 'center', marginTop: 4 }}>Изменения за период</Typography>
        </Grid>
        
        {/* За последний день */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ backgroundColor: '#f1f8e9', boxShadow: 2 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Изменения за день</Typography>
              <Typography>Распознано объектов: {stats.changes.day.recognized_objects}</Typography>
              <Typography>Загруженные фотографии: {stats.changes.day.photos_uploaded}</Typography>
              <Typography>Найдено дефектов: {stats.changes.day.detected_defects}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* За последнюю неделю */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ backgroundColor: '#fff3e0', boxShadow: 2 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Изменения за неделю</Typography>
              <Typography>Распознано объектов: {stats.changes.week.recognized_objects}</Typography>
              <Typography>Загруженные фотографии: {stats.changes.week.photos_uploaded}</Typography>
              <Typography>Найдено дефектов: {stats.changes.week.detected_defects}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* За последний месяц */}
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ backgroundColor: '#ede7f6', boxShadow: 2 }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Изменения за месяц</Typography>
              <Typography>Распознано объектов: {stats.changes.month.recognized_objects}</Typography>
              <Typography>Загруженные фотографии: {stats.changes.month.photos_uploaded}</Typography>
              <Typography>Найдено дефектов: {stats.changes.month.detected_defects}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StatisticsPage;
