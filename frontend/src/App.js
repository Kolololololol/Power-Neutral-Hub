import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemText, CssBaseline, Box } from '@mui/material';
import FileUploadPage from './FileUploadPage';
import HistoryPage from './HistoryPage';
import StatisticsPage from './StatisticsPage';

const drawerWidth = 240;

function App() {
  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />

        {/* Верхняя панель */}
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div">
              Neutral Hub
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Боковая панель */}
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              {[
                { text: 'Загрузка', route: '/' },
                { text: 'История', route: '/history' },
                { text: 'Статистика', route: '/statistics' },
              ].map((item, index) => (
                <ListItem
                  button
                  component={Link}
                  to={item.route}
                  key={index}
                  sx={{
                    textDecoration: 'none',
                    color: 'inherit',
                    '&:hover': {
                      backgroundColor: '#f5f5f5', // Пример: изменение цвета фона при наведении
                    },
                    '&.active': {
                      backgroundColor: '#e0e0e0', // Пример: цвет при активном элементе
                    },
                  }}
                >
                  <ListItemText primary={item.text} />
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* Основная часть */}
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Routes>
            <Route path="/" element={<FileUploadPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/statistics" element={<StatisticsPage />} />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
