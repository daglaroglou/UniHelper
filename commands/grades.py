import json
import os
import nextcord
from nextcord.ext import commands
from datetime import datetime

class GradesView(nextcord.ui.View):
    def __init__(self, embeds, timeout=180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    @nextcord.ui.button(label="<-", style=nextcord.ButtonStyle.gray)
    async def previous_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @nextcord.ui.button(label="->", style=nextcord.ButtonStyle.gray)
    async def next_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @nextcord.ui.button(label="[X]", style=nextcord.ButtonStyle.red)
    async def stop_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        self.stop()
        await interaction.message.delete()

class Grades(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _load_student_data(self, user_id: str):
        file_path = f"students/{user_id}.json"
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_overview_embed(self, data):
        student = data['student']
        embed = nextcord.Embed(
            title="Grade Overview",
            color=nextcord.Color.light_grey(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Student",
            value=f"`{student['firstName']} {student['lastName']}`",
            inline=True
        )
        
        embed.add_field(
            name="Student No",
            value=f"`{student['studentNo']}`",
            inline=True
        )
        
        embed.add_field(
            name="Overall Average",
            value=f"`{data['overallAverage']}`",
            inline=True
        )
        
        embed.add_field(
            name="Total ECTS",
            value=f"`{data['overallECTS']}`",
            inline=True
        )
        
        passed_courses = sum(
            1 for year in data['years'] 
            for semester in year['semesters'] 
            for course in semester['courses'] 
            if course['passed']
        )
        total_courses = sum(
            len(semester['courses']) 
            for year in data['years'] 
            for semester in year['semesters']
        )
        
        embed.add_field(
            name="Courses Passed",
            value=f"`{passed_courses}/{total_courses}`",
            inline=True
        )
        
        if 'updatedAt' in data:
            updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
            embed.add_field(
                name="Last Updated",
                value=f"`{updated_at.strftime('%Y-%m-%d %H:%M')}`",
                inline=True
            )
        
        embed.set_footer(text="Page 1 • Use buttons to navigate semesters")
        
        return embed

    def _create_semester_embed(self, semester_data, semester_name, page_num, total_pages):
        embed = nextcord.Embed(
            title=f"{semester_name}",
            color=nextcord.Color.light_grey(),
            timestamp=datetime.now()
        )
        
        courses = semester_data['courses']
        semester_ects = sum(course['ects'] for course in courses if course['passed'])
        passed = sum(1 for course in courses if course['passed'])
        
        grades = [course['grade'] for course in courses if course['grade'] > 0]
        semester_avg = round(sum(grades) / len(grades), 2) if grades else 0
        
        embed.add_field(
            name="Semester Average",
            value=f"`{semester_avg}`",
            inline=True
        )
        
        embed.add_field(
            name="ECTS Earned",
            value=f"`{semester_ects}`",
            inline=True
        )
        
        embed.add_field(
            name="Passed",
            value=f"`{passed}/{len(courses)}`",
            inline=True
        )
        
        for course in courses:
            status = "✓" if course['passed'] else "✗"
            grade_display = f"{course['grade']}" if course['grade'] != 0 else 0
            
            embed.add_field(
                name=f"{status} {course['courseName']}",
                value=f"`Grade: {grade_display} | ECTS: {course['ects']}`",
                inline=False
            )
        
        embed.set_footer(text=f"Page {page_num}/{total_pages} • Use buttons to navigate")
        
        return embed

    @nextcord.slash_command(name="grades", description="View your grades")
    async def grades(self, interaction: nextcord.Interaction):
        user_id = str(interaction.user.id)
        data = self._load_student_data(user_id)
        
        if not data:
            await interaction.response.send_message(embed=nextcord.Embed(
                title="No Data Found", description="No grade data found. Please login first using `/login`!", color=nextcord.Color.red()
            ), ephemeral=True)
            return
        
        embeds = []
        embeds.append(self._create_overview_embed(data))
        
        page_num = 2
        for year in data['years']:
            for semester_data in year['semesters']:
                semester_name = f"{year['year']} - {semester_data['semester']}"
                total_pages = 1 + sum(len(y['semesters']) for y in data['years'])
                embed = self._create_semester_embed(
                    semester_data, 
                    semester_name, 
                    page_num, 
                    total_pages
                )
                embeds.append(embed)
                page_num += 1
        
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0])
        else:
            view = GradesView(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view)

def setup(bot: commands.Bot):
    bot.add_cog(Grades(bot))
