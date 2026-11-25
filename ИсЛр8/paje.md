# lr10
## 1
### схема?


<Window Title="Управление Базой Данных SQLite" Width="1024" Height="600">
    <!-- Нарезка сетки: задаем пропорции колонок и строк -->
    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="3*" /> <!-- Column 0: Таблицы -->
            <ColumnDefinition Width="1*" /> <!-- Column 1: Панели управления -->
        </Grid.ColumnDefinitions>
        <Grid.RowDefinitions>
            <RowDefinition Height="1*" />    <!-- Row 0: Родительская зона -->
            <RowDefinition Height="1*" />    <!-- Row 1: Дочерняя зона -->
            <RowDefinition Height="Auto" />  <!-- Row 2: Статус-бар -->
        </Grid.RowDefinitions>
        
        <!-- ================= ЛЕВАЯ СТОРОНА (ТАБЛИЦЫ) ================= -->
        
        <!-- Родительская таблица (Верхний левый угол) -->
        <LabelFrame Grid.Row="0" Grid.Column="0" Header="Преподаватели" Margin="5">
            <Treeview Name="tree_teachers">
                <Treeview.Columns>
                    <Column Header="ID" />
                    <Column Header="ФИО" />
                    <Column Header="Кафедра" />
                </Treeview.Columns>
            </Treeview>
        </LabelFrame>
            
        <!-- Дочерняя таблица (Нижний левый угол) -->
        <LabelFrame Grid.Row="1" Grid.Column="0" Header="Предметы" Margin="5">
            <Treeview Name="tree_subjects">
                <Treeview.Columns>
                    <Column Header="ID" />
                    <Column Header="Название" />
                    <Column Header="Часы" />
                    <Column Header="Преподаватель" />
                </Treeview.Columns>
            </Treeview>
        </LabelFrame>

        <!-- ================= ПРАВАЯ СТОРОНА (КНОПКИ) ================= -->
        
        <!-- Управление родительской таблицей (Верхний правый угол) -->
        <LabelFrame Grid.Row="0" Grid.Column="1" Header="Управление преподавателями" Margin="5">
            <Button Content="Добавить преподавателя" Click="on_add_teacher_click" />
        </LabelFrame>
            
        <!-- Поиск и управление дочерней таблицей (Нижний правый угол) -->
        <LabelFrame Grid.Row="1" Grid.Column="1" Header="Управление предметами и Поиск" Margin="5">
            <StackPanel>
                <!-- Секция поиска -->
                <GroupBox Header="Поиск">
                    <TextBox Name="entry_search" Placeholder="Ключевое слово..."/>
                    <Button Content="Найти" Click="on_search_click" />
                    <Button Content="Сбросить" Click="on_reset_click" />
                </GroupBox>
                <!-- Секция CRUD дочерней таблицы -->
                <Button Content="Добавить предмет" Click="on_add_subject_click" />
                <Button Content="Редактировать предмет" Click="on_edit_subject_click" />
                <Button Content="Удалить предмет" Click="on_delete_subject_click" />
            </StackPanel>
        </LabelFrame>
        
        <!-- ================= НИЖНЯЯ ПАНЕЛЬ ================= -->
        <StatusBar Grid.Row="2" Grid.Column="0" Grid.ColumnSpan="2">
            <StatusBarItem Content="Готово. Подключено к БД." />
        </StatusBar>
        
    </Grid>
</Window>
### пу..
![скрин](ресурс1.png)