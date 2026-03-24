"""House-by-house readings based on sign, lord, and occupying planets."""
from kundli.calc import SIGNS

from kundli.names import SIGN_LORDS

HOUSE_THEMES = {
    1: ("Self & Personality", "identity, physical body, temperament, overall life direction"),
    2: ("Wealth & Family", "finances, speech, family values, food habits, early education"),
    3: ("Courage & Siblings", "communication, short travels, siblings, willpower, hobbies"),
    4: ("Home & Mother", "domestic life, mother, property, vehicles, inner peace, education"),
    5: ("Children & Creativity", "children, romance, intelligence, past-life merit, speculation"),
    6: ("Health & Enemies", "illness, debts, enemies, service, daily work, obstacles"),
    7: ("Marriage & Partnerships", "spouse, business partners, public dealings, foreign travel"),
    8: ("Transformation & Longevity", "sudden events, inheritance, occult, chronic illness, research"),
    9: ("Fortune & Dharma", "luck, higher learning, father, long journeys, spirituality, guru"),
    10: ("Career & Status", "profession, reputation, authority, public image, achievements"),
    11: ("Gains & Aspirations", "income, social network, elder siblings, fulfillment of desires"),
    12: ("Loss & Liberation", "expenses, foreign lands, isolation, spirituality, sleep, moksha"),
}

# Planet effects when placed in a house (general interpretations)
PLANET_IN_HOUSE = {
    "Surya": {
        1: "Strong personality and leadership qualities. Confident self-expression.",
        2: "Wealth through authority or government. Firm speech, possible ego in family.",
        3: "Courageous and bold communicator. Good relations with siblings.",
        4: "Desire for a prestigious home. Possible tension with mother.",
        5: "Creative intelligence, interest in politics or leadership roles.",
        6: "Ability to overcome enemies. Good vitality, success in competition.",
        7: "Dominant in partnerships. Spouse may be authoritative or well-placed.",
        8: "Interest in hidden knowledge. Possible health concerns, transformative life events.",
        9: "Strong moral compass, connection with father, drawn to philosophy.",
        10: "Excellent for career and public recognition. Natural authority figure.",
        11: "Gains through government or authority. Influential social circle.",
        12: "Spiritual inclination, possible foreign connections. Ego dissolution over time.",
    },
    "Chandra": {
        1: "Emotional, nurturing personality. Fluctuating moods, adaptable nature.",
        2: "Wealth fluctuates. Sweet speech, attachment to family and food.",
        3: "Imaginative communicator. Emotional bond with siblings.",
        4: "Strong attachment to home and mother. Emotional security through property.",
        5: "Creative and romantic mind. Strong emotional bond with children.",
        6: "Emotional stress from enemies or illness. Service-oriented mindset.",
        7: "Seeks emotional connection in partnerships. Caring spouse.",
        8: "Emotional turbulence, intuitive abilities. Interest in mysteries.",
        9: "Spiritually inclined, love for travel. Emotional connection to beliefs.",
        10: "Public-facing career, popularity. Emotional investment in profession.",
        11: "Gains through public or women. Wide social network.",
        12: "Vivid dreams, spiritual tendencies. Possible foreign residence.",
    },
    "Mangal": {
        1: "Energetic, assertive, competitive personality. Manglik effects on marriage.",
        2: "Harsh speech, aggressive earning style. Possible family conflicts.",
        3: "Very courageous, athletic. Excellent willpower and initiative.",
        4: "Disputes over property. Restless domestic life, strong-willed mother.",
        5: "Competitive children, interest in sports. Impulsive in romance.",
        6: "Excellent placement, defeats enemies, strong immunity, competitive edge.",
        7: "Passionate but potentially conflictual marriage. Manglik consideration.",
        8: "Accident-prone, interest in surgery or occult. Transformative energy.",
        9: "Aggressive pursuit of beliefs. Possible conflicts with father or guru.",
        10: "Ambitious career in engineering, military, or sports. Action-oriented leader.",
        11: "Gains through courage and competition. Influential elder siblings.",
        12: "Hidden anger, expenses on disputes. Possible foreign residence.",
    },
    "Budh": {
        1: "Witty, communicative, youthful appearance. Quick learner.",
        2: "Skilled speaker, good with finances. Intellectual family environment.",
        3: "Excellent communicator, writer, or media person. Good with hands.",
        4: "Intellectual home environment. Interest in education and learning.",
        5: "Sharp intellect, good in studies. Clever children.",
        6: "Analytical problem-solver. Good at handling disputes and health matters.",
        7: "Business-minded partnerships. Communicative spouse.",
        8: "Research-oriented mind. Interest in astrology, investigation.",
        9: "Scholar, teacher, or writer. Love for learning and travel.",
        10: "Career in communication, writing, trade, or technology.",
        11: "Gains through intellect and networking. Diverse friend circle.",
        12: "Imaginative thinker, possible foreign education. Overthinking tendency.",
    },
    "Guru": {
        1: "Wise, optimistic, generous personality. Good health and fortune.",
        2: "Wealth through knowledge. Truthful speech, prosperous family.",
        3: "Wise communicator, helpful siblings. Interest in teaching.",
        4: "Blessed with property, vehicles, and domestic happiness.",
        5: "Excellent for children, education, and spiritual merit. Creative wisdom.",
        6: "Overcomes obstacles through wisdom. May gain weight, generous to a fault.",
        7: "Wise and supportive spouse. Successful partnerships.",
        8: "Long life, interest in occult wisdom. Inheritance possible.",
        9: "Highly auspicious, strong dharma, luck, and spiritual growth.",
        10: "Respected career, possibly in law, education, or advisory roles.",
        11: "Abundant gains, fulfillment of desires. Wise social circle.",
        12: "Spiritual liberation, charitable nature. Possible foreign pilgrimage.",
    },
    "Shukra": {
        1: "Attractive, charming, artistic personality. Love of comfort.",
        2: "Wealth through arts or luxury. Sweet speech, good food habits.",
        3: "Artistic hobbies, creative communication. Harmonious with siblings.",
        4: "Beautiful home, luxury vehicles. Strong bond with mother.",
        5: "Romantic, creative, artistic children. Love affairs.",
        6: "Challenges in relationships. May overcome enemies through diplomacy.",
        7: "Excellent for marriage, loving, attractive spouse. Strong partnerships.",
        8: "Interest in tantric arts, hidden wealth. Sensual transformation.",
        9: "Love for culture, travel, and philosophy. Artistic spiritual path.",
        10: "Career in arts, entertainment, fashion, or luxury goods.",
        11: "Gains through women, arts, or luxury. Fulfillment of desires.",
        12: "Pleasures of the bed, foreign luxury. Spiritual love.",
    },
    "Shani": {
        1: "Disciplined, serious, hardworking. Slow start but steady growth.",
        2: "Frugal with money, delayed wealth. Measured speech.",
        3: "Persistent effort, possible distant siblings. Endurance in communication.",
        4: "Delayed property or domestic happiness. Responsibility toward mother.",
        5: "Delayed children, serious intellect. Structured creativity.",
        6: "Strong placement, defeats enemies through persistence. Chronic health awareness.",
        7: "Delayed or mature marriage. Responsible, older, or serious spouse.",
        8: "Long life through discipline. Interest in deep research. Chronic issues possible.",
        9: "Structured spiritual path. Possible distance from father. Late-blooming luck.",
        10: "Excellent for career, slow rise to authority. Discipline brings success.",
        11: "Steady gains over time. Reliable but small social circle.",
        12: "Isolation, foreign residence, spiritual discipline. Karmic debts.",
    },
    "Rahu": {
        1: "Unconventional personality, ambitious, worldly desires. Mysterious aura.",
        2: "Unusual family dynamics, foreign food habits. Deceptive speech possible.",
        3: "Bold communicator, unconventional hobbies. Success through media.",
        4: "Foreign property or unusual home. Restless domestic life.",
        5: "Unconventional romance, speculative gains. Unusual children.",
        6: "Powerful against enemies. Success in foreign or unconventional healing.",
        7: "Foreign or unconventional spouse. Intense partnerships.",
        8: "Deep interest in occult, sudden transformations. Research ability.",
        9: "Unorthodox beliefs, foreign guru. Breaks from tradition.",
        10: "Ambitious career, fame through unconventional means. Political skill.",
        11: "Large gains, powerful network. Fulfillment through worldly means.",
        12: "Foreign residence, spiritual confusion or awakening. Hidden desires.",
    },
    "Ketu": {
        1: "Spiritual, detached personality. Past-life wisdom, mysterious nature.",
        2: "Detachment from family or wealth. Unusual speech patterns.",
        3: "Intuitive communicator, mystical hobbies. Distant siblings.",
        4: "Detachment from home or mother. Inner spiritual peace.",
        5: "Spiritual intelligence, detachment from children or romance.",
        6: "Excellent for overcoming enemies and illness. Spiritual healing.",
        7: "Detachment in marriage, past-life karmic partnerships.",
        8: "Strong occult abilities, sudden spiritual insights. Moksha karaka.",
        9: "Deep spiritual seeker, past-life dharma. Unconventional beliefs.",
        10: "Detachment from career ambition. Success through spiritual or healing work.",
        11: "Detachment from material gains. Spiritual social circle.",
        12: "Excellent for moksha and liberation. Deep meditation, past-life closure.",
    },
}

# Dasha lord influence on houses
DASHA_EFFECTS = {
    "Surya": "authority, government matters, father, health vitality",
    "Chandra": "emotions, mother, public life, mental peace, travel",
    "Mangal": "energy, courage, property, siblings, conflicts",
    "Budh": "communication, business, intellect, education, trade",
    "Guru": "wisdom, expansion, children, fortune, spirituality",
    "Shukra": "love, luxury, arts, marriage, comfort, vehicles",
    "Shani": "discipline, delays, hard work, karma, chronic matters",
    "Rahu": "worldly ambition, foreign connections, unconventional paths",
    "Ketu": "spiritual growth, detachment, past-life karma, liberation",
}

# Simple house descriptions for general mode
HOUSE_SIMPLE = {
    1: "This house represents your core identity, the way you present yourself to the world, your physical constitution, and the overall direction your life takes. It is the foundation of your entire chart.",
    2: "This house governs your relationship with money, material possessions, family bonds, and the way you communicate. It also reflects your values, eating habits, and early childhood environment.",
    3: "This house reflects your inner courage, your bond with siblings, your communication style, short journeys, and the hobbies or skills you develop through personal effort and initiative.",
    4: "This house represents your home environment, emotional foundation, relationship with your mother, property and vehicles, formal education, and the sense of inner peace you carry within.",
    5: "This house governs romantic relationships, children, creative self-expression, intellectual abilities, and the merit you carry from past lives. It is the house of joy and inspiration.",
    6: "This house deals with your physical health, daily work routine, ability to overcome obstacles, debts, legal disputes, and the service you provide to others through your profession.",
    7: "This house represents marriage, committed partnerships, business collaborations, and your ability to connect with others on a deep, one-to-one level. It also relates to foreign travel.",
    8: "This house governs major life transformations, unexpected events, inheritance, hidden knowledge, chronic health conditions, and your capacity for deep research and investigation.",
    9: "This house represents fortune, higher education, long-distance travel, your relationship with your father, spiritual beliefs, and the guidance you receive from teachers and mentors.",
    10: "This house is the pinnacle of your chart, governing your career, professional reputation, public image, authority, and the lasting achievements you build over your lifetime.",
    11: "This house governs your income beyond salary, social networks, friendships, elder siblings, and the fulfillment of your deepest aspirations and long-term goals.",
    12: "This house represents expenses, foreign lands, solitude, spiritual liberation, the subconscious mind, sleep patterns, and the process of letting go of material attachments.",
}

# Simple planet-in-house readings for general mode (plain language)
SIMPLE_PLANET_IN_HOUSE = {
    "Surya": {
        1: "You have a strong, confident personality. People notice you when you walk into a room.",
        2: "You can earn well, especially through leadership roles. You speak with authority.",
        3: "You're brave and expressive. You likely have a good bond with siblings.",
        4: "You want a nice home and status. There may be some ups and downs with your mother.",
        5: "You're naturally creative and intelligent. You may be drawn to leadership or politics.",
        6: "You're good at overcoming obstacles. Your health and energy are generally strong.",
        7: "You tend to take charge in relationships. Your partner may be strong-willed too.",
        8: "You're drawn to deep or hidden knowledge. Life may bring some unexpected changes.",
        9: "You have strong values and beliefs. You may have a meaningful bond with your father.",
        10: "Great for your career! You're likely to gain recognition and respect at work.",
        11: "You can earn well through connections and influence. You attract powerful friends.",
        12: "You have a spiritual side. You may spend time abroad or enjoy solitude.",
    },
    "Chandra": {
        1: "You're emotional, caring, and intuitive. Your moods may change often.",
        2: "Your finances may go up and down. You love good food and are close to family.",
        3: "You have a vivid imagination. You're emotionally connected to your siblings.",
        4: "Home and family mean everything to you. You're very close to your mother.",
        5: "You're romantic and creative at heart. You'll have a deep bond with your children.",
        6: "You may sometimes feel stressed or worried. Helping others gives you peace.",
        7: "You seek deep emotional connection in relationships. Your partner is likely caring.",
        8: "You may go through emotional ups and downs, but you have strong intuition.",
        9: "You're spiritually inclined and love to travel. Your beliefs are heartfelt.",
        10: "You may have a public-facing career. People are drawn to your warmth.",
        11: "You have a wide social circle. Friendships bring you joy and support.",
        12: "You have vivid dreams and a rich inner life. You may live abroad at some point.",
    },
    "Mangal": {
        1: "You're energetic, bold, and competitive. You like to take action and lead.",
        2: "You can be direct in speech. You earn through hard work and determination.",
        3: "You're very courageous and athletic. You have strong willpower.",
        4: "There may be some restlessness at home. You or your mother are strong-willed.",
        5: "You're competitive and passionate. You may enjoy sports or adventurous hobbies.",
        6: "This is a strong position, you can overcome any challenge or competition.",
        7: "Your relationships are passionate. There may be occasional disagreements.",
        8: "Life may bring sudden changes. You're drawn to investigation or deep subjects.",
        9: "You pursue your beliefs with intensity. You may have a complex relationship with your father.",
        10: "You're ambitious and action-oriented in your career. Great for engineering, sports, or military.",
        11: "You achieve your goals through courage. You may have influential older siblings.",
        12: "You may hold onto frustration. Travel abroad or physical activity helps you release it.",
    },
    "Budh": {
        1: "You're witty, smart, and look younger than your age. You learn things quickly.",
        2: "You're good with words and money. Your family values education.",
        3: "You're an excellent communicator, writing, speaking, or media could suit you well.",
        4: "Your home is a place of learning. You value education and intellectual growth.",
        5: "You're sharp and do well in studies. Your children may be clever too.",
        6: "You're great at solving problems and analyzing situations logically.",
        7: "You're business-minded in partnerships. Your partner is likely talkative and smart.",
        8: "You have a research-oriented mind. You may be interested in mysteries or astrology.",
        9: "You love learning and may become a teacher, writer, or scholar.",
        10: "Your career likely involves communication, technology, writing, or business.",
        11: "You earn through your intellect and connections. You have a diverse friend circle.",
        12: "You're an imaginative thinker. You may study or work abroad.",
    },
    "Guru": {
        1: "You're wise, generous, and optimistic. People trust and respect you.",
        2: "You attract wealth through knowledge. Your family is likely well-off or supportive.",
        3: "You communicate with wisdom. You may enjoy teaching or mentoring.",
        4: "You're blessed with a comfortable home and happiness from your mother.",
        5: "Excellent for education and children. You have natural wisdom and creativity.",
        6: "You overcome problems through wisdom, though you may be too generous at times.",
        7: "Your partner is likely wise and supportive. Relationships bring growth.",
        8: "You may live a long life. You're interested in deep or spiritual knowledge.",
        9: "This is one of the best positions, you're naturally lucky, spiritual, and wise.",
        10: "You'll have a respected career, possibly in teaching, law, or advisory roles.",
        11: "Your wishes tend to come true. You attract abundance and wise friends.",
        12: "You have a charitable and spiritual nature. Pilgrimages or foreign travel are likely.",
    },
    "Shukra": {
        1: "You're attractive, charming, and love beautiful things. People are drawn to you.",
        2: "You enjoy good food and luxury. You can earn well through arts or beauty.",
        3: "You have artistic hobbies and get along well with siblings.",
        4: "Your home is beautiful and comfortable. You have a loving bond with your mother.",
        5: "You're romantic and creative. Love and artistic expression come naturally to you.",
        6: "Relationships may face some challenges, but you handle conflicts with grace.",
        7: "Great for marriage! Your partner is likely attractive and loving.",
        8: "You may discover hidden talents or wealth. You're drawn to deep experiences.",
        9: "You love culture, art, and travel. Your spiritual path has an artistic quality.",
        10: "Your career may involve arts, fashion, entertainment, or luxury.",
        11: "You gain through social connections and creative pursuits. Your desires get fulfilled.",
        12: "You enjoy comfort and may spend on luxuries. Foreign travel brings pleasure.",
    },
    "Shani": {
        1: "You're disciplined and hardworking. Life starts slow but gets better with age.",
        2: "You're careful with money. Wealth comes slowly but steadily through effort.",
        3: "You're persistent and never give up. Communication improves over time.",
        4: "Home happiness may come later in life. You feel responsible for your mother.",
        5: "Children or creative projects may come later. You have a serious, deep intellect.",
        6: "Strong position, you can defeat any obstacle through sheer persistence.",
        7: "Marriage may come later or your partner is mature and responsible.",
        8: "You may live a long life. You're drawn to deep research and serious subjects.",
        9: "Your spiritual growth is structured and disciplined. Luck improves with age.",
        10: "Excellent for career, you rise slowly but surely to positions of authority.",
        11: "Your income grows steadily over time. You have a small but loyal friend circle.",
        12: "You may spend time in solitude or abroad. Spiritual discipline brings peace.",
    },
    "Rahu": {
        1: "You're unique and ambitious. You don't follow the crowd, you make your own path.",
        2: "Your family life may be unconventional. You may enjoy foreign cuisines or cultures.",
        3: "You're a bold communicator. You may find success through media or technology.",
        4: "Your home life may be unusual. You might live in a foreign place.",
        5: "Your love life and creativity are unconventional. You think outside the box.",
        6: "You're powerful against competition. You may succeed in foreign or unusual fields.",
        7: "Your partner may be from a different background. Relationships are intense.",
        8: "You're fascinated by mysteries and hidden knowledge. Life brings sudden changes.",
        9: "You may question traditional beliefs. A foreign teacher or philosophy may guide you.",
        10: "You're very ambitious in your career. You may achieve fame through unusual means.",
        11: "You can achieve big gains and build a powerful network of connections.",
        12: "You may live abroad. Your spiritual journey may be unconventional.",
    },
    "Ketu": {
        1: "You have a spiritual and mysterious quality. You may feel different from others.",
        2: "You're not very attached to money or possessions. Simplicity appeals to you.",
        3: "You have strong intuition. Your hobbies may be unusual or spiritual.",
        4: "You may feel detached from your hometown. Inner peace matters more than material comfort.",
        5: "You have deep spiritual intelligence. Romance may not be your top priority.",
        6: "You're naturally good at overcoming health issues and enemies. Healing comes naturally.",
        7: "Relationships may feel karmic, like you've known your partner before.",
        8: "You have strong intuitive and spiritual abilities. You're drawn to the mystical.",
        9: "You're a deep spiritual seeker. Your beliefs may be unconventional but sincere.",
        10: "Career ambition isn't your main drive. You may succeed through healing or spiritual work.",
        11: "Material gains aren't your focus. Your social circle may be spiritually oriented.",
        12: "This is a powerful spiritual position. Meditation and inner work come naturally to you.",
    },
}

# Simple dasha descriptions for general mode
SIMPLE_DASHA_EFFECTS = {
    "Surya": "a time focused on confidence, leadership, and your relationship with authority figures and father",
    "Chandra": "a time focused on emotions, mother, home life, and your mental well-being",
    "Mangal": "a time of energy, action, and courage, but watch out for conflicts and impatience",
    "Budh": "a time for learning, communication, business, and intellectual growth",
    "Guru": "a time of wisdom, good fortune, spiritual growth, and expansion in life",
    "Shukra": "a time for love, relationships, comfort, creativity, and enjoying life's pleasures",
    "Shani": "a time of hard work, discipline, and patience, rewards come slowly but are lasting",
    "Rahu": "a time of ambition, new experiences, and unconventional opportunities",
    "Ketu": "a time of spiritual growth, letting go of attachments, and inner transformation",
}

# What the dasha lord's energy brings to each house theme (plain language)
DASHA_HOUSE_INFLUENCE = {
    "Surya": {
        1: "You may feel a surge in confidence and self-identity. People notice you more. It's a good time to step into leadership roles and assert who you really are.",
        2: "Your finances may improve through authority or government-related work. Family matters come into focus, you may take a more dominant role in family decisions.",
        3: "Your communication becomes bolder and more authoritative. Courage increases. Good time for writing, media, or starting a new hobby.",
        4: "Home and property matters get attention. You may renovate, buy property, or feel a stronger connection to your roots. Watch for ego clashes at home.",
        5: "Creativity and intelligence shine. Romance may heat up. If you have children, they may achieve something notable. Good for education and speculative ventures.",
        6: "You gain the strength to overcome obstacles, health issues, or workplace challenges. Competition works in your favor. Your vitality is strong.",
        7: "Partnerships and marriage get a spotlight. You or your partner may take on a more dominant role. Business partnerships may form or transform.",
        8: "Expect some transformative life events. Hidden matters may surface. Interest in deep knowledge or research increases. Health needs attention.",
        9: "Your connection with your father or a mentor strengthens. Higher education, travel, or spiritual pursuits bring growth. Luck improves.",
        10: "Career gets a major boost. Recognition, promotions, or public visibility increase. You're seen as an authority figure in your field.",
        11: "Income and social connections grow. Your goals start materializing. Influential people enter your network. Gains through government or authority.",
        12: "Spiritual awareness deepens. You may travel abroad or spend time in solitude. Ego softens, making room for inner growth. Watch expenses.",
    },
    "Chandra": {
        1: "Your emotions are heightened and you become more intuitive. Others find you approachable and nurturing. Your appearance or health may fluctuate.",
        2: "Finances may go up and down. Family bonds strengthen. You may spend more on food, comfort, or family needs. Your speech becomes more emotional.",
        3: "Your imagination and creative communication peak. Emotional bonds with siblings deepen. Short trips bring emotional satisfaction.",
        4: "Home becomes your sanctuary. Strong emotional connection with mother. You may buy property, a vehicle, or invest in making your home more comfortable.",
        5: "Romance and creativity flourish. Emotional bonds with children deepen. Your mind is imaginative and fertile, great for artistic or creative projects.",
        6: "You may feel emotionally stressed by work or health issues. Service to others brings peace. Focus on mental health and emotional balance.",
        7: "Relationships become more emotionally intense. You seek deeper connection with your partner. New partnerships may form based on emotional compatibility.",
        8: "Emotional ups and downs are likely. Your intuition sharpens significantly. You may receive an inheritance or deal with joint finances.",
        9: "Spiritual feelings deepen. Travel brings emotional fulfillment. Your beliefs become more heartfelt. Connection with a guru or teacher is possible.",
        10: "Your career may become more public-facing. Popularity increases. You invest emotionally in your work. Good for careers involving people or nurturing.",
        11: "Social circle expands. Friendships bring emotional support. Income may come through public dealings or women. Your wishes start getting fulfilled.",
        12: "Dreams become vivid and meaningful. Spiritual tendencies increase. You may live or travel abroad. Solitude brings peace rather than loneliness.",
    },
    "Mangal": {
        1: "Your energy and drive increase dramatically. You feel more competitive and assertive. Physical fitness improves. Watch for impatience or aggression.",
        2: "You pursue wealth aggressively. Earning power increases through action and initiative. Be careful with harsh speech, it could cause family friction.",
        3: "Courage and willpower are at their peak. Excellent time for sports, adventure, or starting bold new projects. Sibling relationships are active.",
        4: "Property matters become active, buying, selling, or disputes. Home life may feel restless. Your mother may need attention. Channel energy into home improvement.",
        5: "Passion in romance increases. Competitive spirit helps in education or sports. Children may be more active or demanding. Creative energy is high but impulsive.",
        6: "One of the best periods for defeating competition and overcoming obstacles. Your immunity is strong. Legal matters or disputes resolve in your favor.",
        7: "Relationships become passionate but potentially heated. Marriage may go through an intense phase. Business partnerships require patience and compromise.",
        8: "Life may bring sudden changes or transformations. Be cautious about accidents or health. Interest in surgery, investigation, or occult subjects increases.",
        9: "You pursue your beliefs with intensity. Travel may be adventurous. Relationship with father or guru may have some friction. Physical pilgrimages are favored.",
        10: "Career ambition skyrockets. You take bold action at work. Great for engineering, military, sports, or any action-oriented profession. Leadership opportunities arise.",
        11: "Goals are achieved through courage and determination. Income increases through competitive efforts. Elder siblings may play an important role.",
        12: "Hidden frustrations may surface. Expenses increase, possibly on disputes or travel. Physical activity and spiritual practices help channel this energy positively.",
    },
    "Budh": {
        1: "Your mind becomes sharper and communication skills improve. You appear more youthful and witty. It's a great time for learning new skills and self-improvement.",
        2: "Financial intelligence improves. Good time for business, investments, or financial planning. Your speech becomes more persuasive. Family discussions are productive.",
        3: "Communication is at its best. Writing, media, teaching, or any form of expression brings success. Sibling bonds improve. Short trips are beneficial.",
        4: "Education and intellectual pursuits at home flourish. You may study, take courses, or create an intellectual environment at home. Property paperwork goes smoothly.",
        5: "Intellect and analytical skills peak. Excellent for students, researchers, or anyone in education. Children may excel academically. Romance involves mental connection.",
        6: "Problem-solving abilities are excellent. You can analyze and overcome any challenge. Health awareness improves. Good for medical checkups and addressing chronic issues.",
        7: "Business partnerships thrive. Communication with your spouse improves. Negotiations and contracts are favored. Your partner may be more talkative and engaged.",
        8: "Research and investigation skills sharpen. Interest in astrology, psychology, or hidden knowledge grows. Financial matters involving others (insurance, inheritance) need attention.",
        9: "Higher education, teaching, and publishing are strongly favored. Travel for learning is beneficial. Your philosophical outlook expands. Writing a book or thesis is supported.",
        10: "Career in communication, technology, writing, or trade gets a boost. Your professional reputation grows through your intellect. Networking brings opportunities.",
        11: "Income through intellect, networking, and business connections increases. Your social circle becomes more diverse and intellectually stimulating. Goals materialize through smart planning.",
        12: "Imagination and creative thinking increase. Foreign education or work is possible. You may overthink or worry, meditation and journaling help. Spiritual study is favored.",
    },
    "Guru": {
        1: "Wisdom, optimism, and generosity define this period. Your personality expands. Health improves. People seek your advice. Spiritual growth accelerates.",
        2: "Wealth increases through knowledge and ethical means. Family life is harmonious. Your speech carries wisdom and truth. Good food and comfort come naturally.",
        3: "You communicate with wisdom and authority. Teaching or mentoring opportunities arise. Siblings benefit from your guidance. Creative hobbies bring joy.",
        4: "Domestic happiness increases. Property acquisition is favored. Relationship with mother improves. Education brings fulfillment. Inner peace deepens.",
        5: "One of the best periods for children, education, and creativity. Romance is meaningful. Spiritual merit increases. Investments may do well.",
        6: "You overcome obstacles through wisdom rather than force. Health improves. Legal matters resolve favorably. Be careful about overindulgence or weight gain.",
        7: "Marriage and partnerships flourish. Your spouse is supportive and wise. Business partnerships bring growth. Foreign connections are beneficial.",
        8: "Interest in deep wisdom, occult, or spiritual transformation grows. Longevity is supported. Inheritance or unexpected gains are possible.",
        9: "This is the most auspicious period, luck, dharma, and spiritual growth are at their peak. Higher education, travel, and connection with a guru bring blessings.",
        10: "Career reaches new heights. You gain respect and authority. Roles in education, law, consulting, or advisory positions are favored. Public image shines.",
        11: "Abundance flows in. Your wishes and aspirations start manifesting. Social circle includes wise and influential people. Elder siblings prosper.",
        12: "Spiritual liberation and charitable activities increase. Foreign pilgrimage or travel is likely. You find peace in giving and letting go. Meditation deepens.",
    },
    "Shukra": {
        1: "Your charm and attractiveness increase. You enjoy life's pleasures more. Artistic talents surface. Relationships improve. You invest in your appearance.",
        2: "Wealth increases through arts, luxury, or beauty-related fields. You enjoy good food and comfort. Family life is harmonious and pleasant.",
        3: "Artistic hobbies and creative communication bring joy. Relationships with siblings are harmonious. Short trips are pleasurable. Media or arts projects succeed.",
        4: "Your home becomes more beautiful and comfortable. You may buy a vehicle or renovate. Relationship with mother is loving. Inner happiness increases.",
        5: "Romance is in the air. Creative expression flourishes. Children bring joy. Love affairs may begin or deepen. Artistic projects succeed.",
        6: "Relationships may face some tests, but diplomacy helps you navigate. Health improves through self-care and beauty routines. Workplace becomes more pleasant.",
        7: "Excellent period for marriage and partnerships. Love deepens. Your spouse is supportive and attractive. Business partnerships are profitable and harmonious.",
        8: "Hidden talents or wealth may surface. Sensual experiences deepen. Interest in beauty, art, or tantric subjects grows. Joint finances improve.",
        9: "Love for culture, philosophy, and travel increases. Artistic spiritual practices bring growth. Foreign connections are romantic or culturally enriching.",
        10: "Career in arts, entertainment, fashion, beauty, or luxury thrives. Your professional image becomes more polished and attractive. Creative recognition comes.",
        11: "Gains through social connections, women, or creative fields. Your desires get fulfilled. Social life is vibrant and enjoyable. Friendships bring pleasure.",
        12: "Foreign luxury and travel are likely. Spiritual love and compassion grow. You may spend on comfort and pleasure. Bedroom life improves.",
    },
    "Shani": {
        1: "Life demands discipline and hard work. You may feel more serious or burdened, but this builds lasting character. Health needs attention, stay consistent with routines.",
        2: "Finances require careful management. Wealth comes slowly through persistent effort. You become more measured in speech. Family responsibilities increase.",
        3: "Communication requires more effort but becomes more meaningful. Persistence pays off in hobbies and skills. Sibling relationships may feel distant but deepen over time.",
        4: "Home and property matters may face delays or require extra effort. Responsibility toward mother increases. Patience with domestic issues is essential. Long-term property investments are favored.",
        5: "Creativity takes a more structured form. Romance may feel serious or delayed. Children may need extra attention. Education requires discipline but yields deep understanding.",
        6: "Strong period for defeating long-standing obstacles. Chronic health issues can be addressed. Hard work at your job pays off. Enemies are overcome through persistence.",
        7: "Relationships require patience and maturity. Marriage may feel heavy but grows stronger through commitment. Business partnerships need clear boundaries and responsibilities.",
        8: "Deep transformation through discipline. Interest in research or serious subjects grows. Chronic health matters need attention. Long-term financial planning is essential.",
        9: "Spiritual growth comes through structured practice and discipline. Luck improves slowly. Relationship with father may be distant but respectful. Higher education requires extra effort.",
        10: "Career demands hard work but rewards are lasting. Slow and steady rise to authority. Discipline and reliability earn you respect. This is a career-defining period.",
        11: "Income grows steadily through consistent effort. Social circle may be smaller but more reliable. Long-term goals start materializing. Patience with aspirations pays off.",
        12: "Solitude and spiritual discipline bring growth. Foreign residence is possible. Karmic debts may surface for resolution. Rest and recovery are important.",
    },
    "Rahu": {
        1: "You feel driven by ambition and a desire to stand out. Your personality may undergo an unconventional transformation. New, unexpected opportunities arise.",
        2: "Finances may come through unusual or foreign sources. Family dynamics shift. You may develop new tastes or habits. Watch for deceptive financial schemes.",
        3: "Bold and unconventional communication brings success. Media, technology, or foreign connections open doors. You take risks that others wouldn't.",
        4: "Home life may change unexpectedly. Foreign property or unusual living arrangements are possible. Restlessness at home pushes you toward new experiences.",
        5: "Romance and creativity take unconventional turns. Speculative gains are possible but risky. Your thinking becomes innovative and outside-the-box.",
        6: "Powerful period for overcoming enemies and competition. Unconventional healing or foreign medical treatment may help. You find success where others see obstacles.",
        7: "Partnerships may involve foreign or unconventional people. Marriage goes through an intense, transformative phase. Business opportunities come from unexpected sources.",
        8: "Deep fascination with mysteries, occult, or hidden knowledge. Life brings sudden transformations. Research abilities peak. Joint finances may change unexpectedly.",
        9: "Your beliefs may shift dramatically. A foreign guru or unconventional philosophy may influence you. Travel to unusual destinations is likely.",
        10: "Career ambition reaches its peak. Fame or recognition through unconventional means. You may enter politics, technology, or foreign-related fields. Bold career moves pay off.",
        11: "Large gains and powerful networking opportunities. Your social circle expands dramatically. Ambitious goals start manifesting. Foreign connections bring profit.",
        12: "Foreign residence or travel is strongly indicated. Spiritual journey may be confusing but ultimately enlightening. Hidden desires surface for resolution.",
    },
    "Ketu": {
        1: "You feel more introspective and spiritually aware. Material ambitions take a back seat. Others may find you mysterious. Past-life patterns surface for healing.",
        2: "Attachment to money and possessions loosens. Family dynamics may shift. You find value in simplicity. Speech becomes more thoughtful and less materialistic.",
        3: "Intuition guides your communication. Hobbies may become more spiritual or mystical. Sibling relationships may feel distant but carry deeper meaning.",
        4: "Detachment from material home comforts grows. Inner peace becomes more important than outer luxury. You may relocate or feel restless about your living situation.",
        5: "Spiritual intelligence deepens. Romance may feel karmic or past-life connected. Creative expression takes a mystical turn. Children may teach you spiritual lessons.",
        6: "Natural healing abilities emerge. You overcome enemies and health issues through spiritual strength. Alternative medicine or healing practices attract you.",
        7: "Relationships feel karmic, like unfinished business from past lives. Marriage may go through a spiritual transformation. Detachment helps improve partnerships.",
        8: "Powerful spiritual awakening is possible. Intuitive and occult abilities strengthen. Sudden insights change your perspective on life. Deep meditation brings breakthroughs.",
        9: "Deep spiritual seeking defines this period. Your beliefs become more personal and less conventional. Past-life dharma activates. Pilgrimages bring profound experiences.",
        10: "Career ambition decreases but spiritual purpose increases. Success comes through healing, spiritual, or service-oriented work. You redefine what success means to you.",
        11: "Material gains aren't your focus, spiritual friendships and meaningful connections matter more. Your social circle may shift toward like-minded spiritual seekers.",
        12: "One of the most powerful periods for spiritual liberation. Meditation, retreat, and inner work bring deep peace. Past-life karma resolves. Moksha energy is strong.",
    },
}


def build_house_readings(planets, houses, dashas, now, planet_house_map=None):
    """Build structured house readings for both general and advanced modes.

    Args:
        planets: list of planet dicts from compute_planets
        houses: list of house dicts from compute_houses
        dashas: list of dasha dicts from compute_dasha
        now: datetime for current dasha detection
        planet_house_map: precomputed {planet_name: house_num}, built if not provided

    Returns:
        (readings_list, current_dasha_lord)
    """
    from kundli.calc import build_planet_house_map, get_aspecting_planets

    if planet_house_map is None:
        planet_house_map = build_planet_house_map(planets, houses)

    current_dasha = None
    for d in dashas:
        if d["start"] <= now <= d["end"]:
            current_dasha = d["lord"]
            break

    def occupants(hnum):
        return [p for p in planets if planet_house_map.get(p["planet"]) == hnum]

    readings = []
    for h in houses:
        num = h["house"]
        sign = h["sign"]
        lord = SIGN_LORDS[sign]
        theme, keywords = HOUSE_THEMES[num]
        occ = occupants(num)
        aspectors = get_aspecting_planets(planets, sign)
        lord_house = planet_house_map.get(lord)

        # Advanced planet readings
        planet_readings = []
        simple_planet_readings = []
        for o in occ:
            planet_readings.append({
                "name": o["planet"],
                "reading": PLANET_IN_HOUSE.get(o["planet"], {}).get(num, ""),
            })
            simple_planet_readings.append({
                "name": o["planet"],
                "reading": SIMPLE_PLANET_IN_HOUSE.get(o["planet"], {}).get(num, ""),
            })

        # Lord note
        lord_note = ""
        if lord_house:
            if lord_house == num:
                lord_note = f"in own house, strengthening all {theme.lower()} matters"
            else:
                lh_theme = HOUSE_THEMES[lord_house][0]
                lord_note = f"in House {lord_house} ({lh_theme}), connecting {theme.lower()} with {lh_theme.lower()}"

        # Dasha notes
        dasha_note = ""
        simple_dasha_note = ""
        current_influence = ""
        if current_dasha:
            dasha_house = planet_house_map.get(current_dasha)
            dasha_effect = DASHA_EFFECTS.get(current_dasha, "")
            simple_effect = SIMPLE_DASHA_EFFECTS.get(current_dasha, "")
            current_influence = DASHA_HOUSE_INFLUENCE.get(current_dasha, {}).get(num, "")
            if dasha_house == num:
                dasha_note = f"Dasha lord sits here, so this house is currently activated ({dasha_effect})"
                simple_dasha_note = f"This area of your life is especially active right now. It's {simple_effect}."
            elif current_dasha == lord:
                dasha_note = f"Dasha is the lord of this house, expect developments in {keywords}"
                simple_dasha_note = "You may notice changes here soon. The current period brings focus to this area."
            elif current_dasha in aspectors:
                dasha_note = f"Dasha lord aspects this house, bringing indirect influence on {theme.lower()}"
                simple_dasha_note = "This area is getting some extra attention during this period of your life."

        # General summary
        simple_summary = HOUSE_SIMPLE[num]
        if occ:
            extras = [SIMPLE_PLANET_IN_HOUSE.get(o["planet"], {}).get(num, "") for o in occ]
            simple_summary += " " + " ".join(s for s in extras if s)

        readings.append({
            "num": num, "sign": sign, "lord": lord, "lord_house": lord_house,
            "theme": theme, "keywords": keywords,
            "occupants": [o["planet"] for o in occ],
            "planet_readings": planet_readings,
            "simple_planet_readings": simple_planet_readings,
            "aspectors": aspectors, "lord_note": lord_note, "dasha_note": dasha_note,
            "simple_summary": simple_summary, "simple_dasha_note": simple_dasha_note,
            "current_influence": current_influence,
        })
    return readings, current_dasha
